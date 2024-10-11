import traceback
import io
import sys
import re
import os
# from .forecasting_model_inference import forecasting_model_inference_api
import requests
import pandas as pd


def login(email='farm@fashion.ai', password='secret'):
        url = 'https://catalog.dev.api.fashionaiale.com/api/v1/auth/email/login'
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


token = login()



def fetch_postgres_data(sql_code):
    sql_code = f'''{sql_code}'''
    base_url = 'https://catalog.dev.api.fashionaiale.com/api/products/query'
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
        print(df.head())
        return df
    else:
        response.raise_for_status()
# Define the base path as a variable


class CustomPythonEnv:
    # Determine the project's root directory dynamically
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Set the default base path to '/User' folder at the root of the project
    default_base_path = os.path.join(project_root, 'Users')

    def __init__(self, base_path=None):
        # Initialize attributes for capturing stdout and errors
        self.output_buffer = io.StringIO()
        self.error_trace = ""
        self.cleaned_traceback = ""
        # Use the provided base_path or the default one
        self.base_path = base_path or CustomPythonEnv.default_base_path

    def _clean_traceback(self, traceback_str, code_str):
        traceback_pattern = re.compile(r'File "<string>", line (\d+), in (.*)')
        filtered_traceback = []

        for line in traceback_str.splitlines():
            match = traceback_pattern.match(line)
            if match:
                line_num, func = match.groups()
                filtered_traceback.append(f'  Line {line_num}, in {func}')
            else:
                filtered_traceback.append(line)

        if filtered_traceback and filtered_traceback[0].startswith('Traceback'):
            filtered_traceback.pop(0)

        return '\n'.join(filtered_traceback)

    def _remove_global_scope_trace(self, traceback_str):
        """
        Removes the portion of the traceback string that contains the file path of the global scope.
        """
        global_scope_pattern = re.compile(r'File ".*?", line \d+, in execute')

        filtered_traceback = [line for line in traceback_str.splitlines() if not global_scope_pattern.search(line)]

        return '\n'.join(filtered_traceback)

    def execute(self, code_str):
        """
        Executes a string of Python code and captures output and errors.
        """
        original_stdout = sys.stdout

        sys.stdout = self.output_buffer

        desired_path = os.path.join(self.base_path, 'agentfiles')
        original_working_directory = os.getcwd()
        os.makedirs(desired_path, exist_ok=True)
        os.chdir(desired_path)

        try:
            exec(code_str, globals())
            combined_output = self.output_buffer.getvalue()
            self.output_buffer = io.StringIO()
            return "Success", combined_output
        except Exception:
            sys.stdout = original_stdout

            self.error_trace = traceback.format_exc()

            self.cleaned_traceback = self._clean_traceback(self.error_trace, code_str)

            self.cleaned_traceback = self._remove_global_scope_trace(self.cleaned_traceback)

            printed_output = self.output_buffer.getvalue()
            combined_output = f"Output before error:\n{printed_output}\nAn error occurred!\n{self.cleaned_traceback}"
            self.output_buffer = io.StringIO()
            return "Error", combined_output
        finally:
            sys.stdout = original_stdout
            os.chdir(original_working_directory)
    


# custom_env = CustomPythonEnv()
# success, result = custom_env.execute("""df = fetch_postgres_data('SELECT "productId", "price", "stock" FROM product WHERE "price" > 100')""")
# print(result)
# code_str = """
# print("Hello World")
# def faulty_function():
#    return 1 / 0


# print(faulty_function())
# """
# status, response = custom_env.execute(code_str)
# print('here: ',status, '\n\n', response)

