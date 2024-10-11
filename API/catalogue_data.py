import requests
import pandas as pd



class CatalogClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.token = token

    def set_token(self, token):
        self.token = token

    def get_products(self, page=1, limit=1000000000):
        url = f"{self.base_url}/api/products/all?page={page}&limit={limit}"
        headers = {
            'accept': '*/*',
            'Authorization': f'Bearer {self.token}'
        }
        response = requests.get(url, headers=headers)
        res = response.json()
        return res['items']
    
    def get_complete_products(self):
        data = []
        for i in range(100):
            products = self.get_products(page=i+1)
            print('Length of product: ', len(products))
            if len(products) < 1:
                break
            data.extend(products)

        df = pd.DataFrame(data)
        df.to_csv('farmrio_catalog.csv')

    def login(self, email, password):
        url = f"https://catalog.dev.api.fashionaiale.com/api/v1/auth/email/login"
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {
            "email": email,
            "password": password
        }
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        if 'token' in response_data:
            self.set_token(response_data['token'])
        return response_data
    

    def prepare_prompt(self):
        PROMPT = """
        You are an helpful assistant

        ## Your role
        Your role is to write python pandas code to answer user question and respond to them

        



        """
    
# catalog = CatalogClient(base_url="https://catalog.dev.api.fashionaiale.com")
# catalog.login(email='farm@fashion.ai', password='secret')
# catalog.get_complete_products()

# df = pd.read_csv('farmrio_catalog.csv')
# print(df.info())
# print(df.head())
# print(df['collections'].unique())
    

