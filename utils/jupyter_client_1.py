import sys
import os
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)
import jupyter_client
from jupyter_client.kernelspec import KernelSpecManager
import time
import requests
import pandas as pd
import inspect
import re
from utils.code_history_manager import code_history_manager

def clean_error_message(error_msg):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    cleaned_msg = ansi_escape.sub('', error_msg)
    lines = cleaned_msg.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    cleaned_msg = '\n'.join(lines)
    return cleaned_msg

# https://catalog.dev.api.fashionaiale.com
CATALOG_URL = os.getenv("CATALOG_URL", "https://catalog.dev.api.fashionaiale.com")

def login(email='farm@fashion.ai', password='secret'):
    CATALOG_URL = os.getenv("CATALOG_URL", "https://catalog.dev.api.fashionaiale.com")
    url = f'{CATALOG_URL}/api/v1/auth/email/login'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    payload = {
        'email': email,
        'password': password
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        result = {
            "token": data['token'],
        }
        return result['token']
    else:
        response.raise_for_status()


token = ""

def fetch_postgres_data(sql_code):
    import requests
    import pandas as pd
    # print('> Token in fetch_postgres_data > ', token)
    
    # def login(email='farm@fashion.ai', password='secret'):
    #     CATALOG_URL = os.getenv("CATALOG_URL", "https://catalog.dev.api.fashionaiale.com")
    #     url = f'{CATALOG_URL}/api/v1/auth/email/login'
    #     headers = {
    #         'accept': 'application/json',
    #         'Content-Type': 'application/json'
    #     }
    #     payload = {
    #         'email': email,
    #         'password': password
    #     }
    #     response = requests.post(url, headers=headers, json=payload)
    #     if response.status_code == 200:
    #         data = response.json()
    #         result = {
    #             "token": data['token'],
    #         }
    #         return result['token']
    #     else:
    #         response.raise_for_status()

    # token = login()

    # token = code_history_manager.

    CATALOG_URL = os.getenv("CATALOG_URL", "https://catalog.dev.api.fashionaiale.com")
    sql_code = f'''{sql_code}'''
    base_url = f'{CATALOG_URL}/api/products/query'
    encoded_query = requests.utils.quote(sql_code)
    url = f'{base_url}?query={encoded_query}'

    headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {token}'
        }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        return df
    else:
        response.raise_for_status()

class JupyterClient:
    def __init__(self):
        self.kernel_spec_manager = KernelSpecManager()
        self.clients = {}
        self.globals = {}  # Dictionary to store global variables for each session
        self.file_save_path = os.path.join("utils", "Users", "agentfiles")

        print(self.file_save_path)

    def get_sessions(self):
        return list(self.clients.keys())

    def create_new_session(self, session_id="anas", kernel_name='python3'):
        if session_id in self.clients.keys():
            return session_id
        km = jupyter_client.KernelManager(kernel_name=kernel_name)
        km.start_kernel()
        client = km.client()
        self.clients[session_id] = (km, client)
        self.globals[session_id] = {}  # Initialize empty globals for this session
        self.import_fetch_postgres_data(session_id=session_id)
        self.set_environment_variable(session_id=session_id)
        return session_id

    def set_global(self, session_id, variable_name, value):
        if session_id not in self.globals:
            raise ValueError(f"Session {session_id} not found")
        self.globals[session_id][variable_name] = value
        self.execute_code(f"{variable_name} = {repr(value)}", session_id)

    def get_global(self, session_id, variable_name):
        if session_id not in self.globals:
            raise ValueError(f"Session {session_id} not found")
        return self.globals[session_id].get(variable_name)

    def import_fetch_postgres_data(self, session_id):
        TOKEN = code_history_manager.get_catalog_token(sid=session_id)
        fetch_postgres_data_code = f'token="""{TOKEN}"""\n'
        fetch_postgres_data_code += inspect.getsource(fetch_postgres_data)
        fetch_postgres_data_code += f"\nprint(token)\nglobals()['fetch_postgres_data'] = fetch_postgres_data" 
        print(fetch_postgres_data_code)       
        result = self.execute_code(fetch_postgres_data_code, session_id)
        
        if "Error" in result:
            print(f"Error importing fetch_postgres_data function: {result}")
        else:
            print("Successfully imported fetch_postgres_data function > ", result)

    def save_file(self, filename, content):
        file_path = os.path.join(self.file_save_path, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path

    def execute_code(self, code, session_id):

        

        if session_id not in self.clients:
            raise ValueError(f"Session {session_id} not found")


        _, client = self.clients[session_id]

        # Prepend code to update globals in the kernel
        globals_code = "\n".join([f"{k} = {repr(v)}" for k, v in self.globals[session_id].items()])
        
        # Inject custom save function
        save_function = f"""
def custom_save(filename, content):
    import os
    file_path = os.path.join("{self.file_save_path}", filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)
    return file_path

# Override built-in open function for writing
original_open = open
def custom_open(file, mode='r', *args, **kwargs):
    if 'w' in mode or 'a' in mode:
        return original_open(custom_save(file, ''), mode, *args, **kwargs)
    return original_open(file, mode, *args, **kwargs)

import builtins
builtins.open = custom_open
"""

        full_code = f"{globals_code}\n{save_function}\n{code}"

        msg_id = client.execute(full_code)

        output = []
        status = "Success"
        timeout = time.time() + 30  # 60 second timeout

        while time.time() < timeout:
            try:
                msg = client.get_iopub_msg(timeout=1)
                if 'parent_header' not in msg:
                    output.append(f"Unexpected message format: {msg}")
                    continue

                if msg['parent_header'].get('msg_id') != msg_id:
                    continue

                msg_type = msg.get('msg_type', '')
                content = msg.get('content', {})

                if msg_type == 'execute_result':
                    output.append(str(content.get('data', {}).get('text/plain', '')))
                elif msg_type == 'stream':
                    output.append(content.get('text', ''))
                elif msg_type == 'error':
                    error_traceback = "\n".join(content.get('traceback', []))
                    cleaned_error = clean_error_message(error_traceback)
                    output.append(f"Error: {cleaned_error}")
                    status = 'Fail'
                elif msg_type == 'status' and content.get('execution_state') == 'idle':
                    break
            except Exception as e:
                pass
                # output.append(f"Exception while getting message: {str(e)}")
                # status = 'Fail'

        if time.time() >= timeout:
            output.append("Execution timed out. Try again")
            status = 'Fail'

        return status, '\n'.join(output).strip()
    
    def set_environment_variable(self, session_id):
        code = f"import os\nos.environ['CATALOG_URL'] = {repr(CATALOG_URL)}"
        success, result = self.execute_code(code, session_id)
        if not success:
            raise RuntimeError(f"Failed to set environment variable: {result}")

    def close_session(self, session_id):
        if session_id not in self.clients:
            raise ValueError(f"Session {session_id} not found")
        
        km, client = self.clients[session_id]
        client.stop_channels()
        km.shutdown_kernel()
        del self.clients[session_id]
        del self.globals[session_id]

    def close_all_sessions(self):
        for session_id in list(self.clients.keys()):
            self.close_session(session_id)





if __name__ == "__main__":
    jc = JupyterClient()

    try:
        session_id = jc.create_new_session("anas")
        print(f"Created new session with ID: {session_id}")

        jc.import_fetch_postgres_data(session_id)

        # Test file saving
        code = """
with open('test.txt', 'w') as f:
    f.write('This is a test file.')
print('File saved successfully.')
"""
        status, result = jc.execute_code(code, session_id)
        print(f"Result of file saving test: {status}, {result}")

        # Test SQL query
        code = "sales_query = '''WITH product_sales AS ( SELECT \"item_productId\", SUM(CAST(\"item_quantity\" AS INTEGER)) AS total_units_sold FROM sales_history GROUP BY \"item_productId\" HAVING total_units_sold > 200) SELECT p.\"title\", p.\"sku\", ps.total_units_sold FROM product p JOIN product_sales ps ON p.\"productId\" = ps.\"item_productId\" LIMIT 10''' products_over_200_sales = fetch_postgres_data(sales_query) products_over_200_sales_count = len(products_over_200_sales) if products_over_200_sales_count <= 10 else products_over_200_sales.to_csv('products_over_200_sales.csv', index=False) products_over_200_sales if products_over_200_sales_count <= 10 else 'More than 10 items'"
        status, result = jc.execute_code(code, session_id)
        print(f"Result of SQL query test: {status}, {result}")

        jc.close_session(session_id)
        print(f"Closed session: {session_id}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        jc.close_all_sessions()
        print("All sessions closed")



# sales_query = '''WITH product_sales AS ( SELECT \"item_productId\", SUM(CAST(\"item_quantity\" AS INTEGER)) AS total_units_sold FROM sales_history GROUP BY \"item_productId\" HAVING total_units_sold > 200) SELECT p.\"title\", p.\"sku\", ps.total_units_sold FROM product p JOIN product_sales ps ON p.\"productId\" = ps.\"item_productId\" ''' 
# products_over_200_sales = fetch_postgres_data(sales_query) 
# products_over_200_sales_count = len(products_over_200_sales) 
# if products_over_200_sales_count <= 10
# else products_over_200_sales.to_csv('products_over_200_sales.csv', index=False) 
# products_over_200_sales if products_over_200_sales_count <= 10 else 'More than 10 items