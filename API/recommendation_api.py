import aiohttp
import aiofiles
import asyncio
import pandas as pd
import openai
from pinecone import Pinecone
from typing import List
import os
import io
from concurrent.futures import ThreadPoolExecutor
import requests
from dotenv import load_dotenv


load_dotenv()

class RecommendationAPI:
    def __init__(self):
        # self.pinecone_client = Pinecone(api_key=api_key_pinecone)
        # self.openai_client = openai
        # self.openai_client.api_key = api_key_openai
        # self.index_name = "farmio-vectors"
        # self.index = self.connect_to_pinecone()
        self.displayed_product = []
        self.executor = ThreadPoolExecutor()

    def connect_to_pinecone(self):
        index = self.pinecone_client.Index(self.index_name)
        return index

    async def fetch_embedding(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        text = text.replace("\n", " ")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self.openai_client.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "input": text
                }
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data['data'][0]['embedding']

    async def join_product(self, json_data: List[dict]) -> str:
        # Load CSV data
        csv_path = "asli_farm.csv"
        async with aiofiles.open(csv_path, mode='r') as f:
            csv_content = await f.read()
            csv_data = pd.read_csv(io.StringIO(csv_content))
        csv_data['product_id'] = csv_data['product_id'].astype(str)

        # Convert JSON data to DataFrame
        json_df = pd.DataFrame(json_data)

        # Join JSON DataFrame with CSV DataFrame on product_id
        joined_df = pd.merge(json_df, csv_data, left_on='product_id', right_on='product_id', how='inner')

        # Select columns: name, price, and url
        selected_columns = joined_df[['name', 'price', 'url']]

        return selected_columns.to_json(orient='records')

    async def recommendation_api(self, user_augmented_requirement: str, budget: List[int] = [10000], color: List[str] = ['any'], size: str = ['any'], categories: List[str] = ["any"]) -> str:
        search_phrase_embedding = await self.fetch_embedding(user_augmented_requirement)

        size = size[0]
        budget = budget[0]
        color = color[0]
        categories = categories[0]

        
        if size == 'S':
            filter = {"S": {"$eq": 1.0}, "product_id": {"$nin": self.displayed_product}}
        elif size == "M":
            filter = {"M": {"$eq": 1.0}, "product_id": {"$nin": self.displayed_product}}
        elif size == "L":
            filter = {"L": {"$eq": 1.0}, "product_id": {"$nin": self.displayed_product}}
        elif size == "XL":
            filter = {"XL": {"$eq": 1.0}, "product_id": {"$nin": self.displayed_product}}
        else:
            filter = {"S": {"$eq": 1.0}, "M": {"$eq": 1.0}, "L": {"$eq": 1.0}, "XL": {"$eq": 1.0}, "product_id": {"$nin": self.displayed_product}}

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            self.executor,
            lambda: self.index.query(
                vector=search_phrase_embedding,
                top_k=10,
                # filter=filter,
                include_values=False,
                include_metadata=True
            )
        )

        if len(results['matches']) < 1:
            return "No Dress Found"

        array = []
        for item in results['matches']:
            self.displayed_product.append(item['id'])
            array.append({'product_id': item['id']})

        retrieved_product = await self.join_product(array)

        return retrieved_product
    
    async def recommendation_api_semantic_search(self, user_augmented_requirement: str, budget: List[int] = [1000000], color: List[str] = [], size: List[str] = [], categories: List[str] = []) -> str:
        url = os.getenv('API_SEMANTIC_SEARCH_URL')+'/search/'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        payload = {
            "query": user_augmented_requirement,
            "colors": color,
            "sizes": size,
            "price": budget[0],
            "categories": categories,
            "client_id": 1,
            "is_category_projection": True,
            "is_taxonomy_projection": False
        }

        response = requests.post(url, headers=headers, json=payload)
        res = response.json()
        return res['product_information'], res['explanation']

# Usage
api_key_pinecone = os.getenv('API_KEY_PINECONE')
api_key_openai = os.getenv('API_KEY_OPEN_AI')
agent = RecommendationAPI()


recommendation_api = agent.recommendation_api_semantic_search


# # Example usage
# query = "I am travelling to India, what should I buy?"
# colors = ["Preto", "Verde", "Amarelo", "Azul", "Bege", "Colorido", "Branco"]
# sizes = ["PP", "GG", "M", "P"]
# price = [20000]
# categories = ["Vestidos", "Camisa", "Camisetas", "Cardigan", "Calças"]
# client_id = 1
# is_category_projection = True
# is_taxonomy_projection = False

# print(recommendation_api(user_augmented_requirement=query, color=colors, size=sizes, budget=price, categories=categories))


# If needed in another module, you can now import recommendation_api:
# from recommendation_module import recommendation_api
