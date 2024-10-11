import os
import aiohttp
import openai
import asyncio
from langchain_community.vectorstores import FAISS
from concurrent.futures import ThreadPoolExecutor

os.environ["OPENAI_API_KEY"] = ''
openai.api_key = os.environ["OPENAI_API_KEY"]

executor = ThreadPoolExecutor()

async def fetch_embedding(text: str) -> list:
    """
    Fetch the embedding for a given text using the OpenAI API.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={
                "model": "text-embedding-ada-002",
                "input": text
            }
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data['data'][0]['embedding']

async def get_company_policy_api(query_string: str) -> str:
    """
    Use this tool to answer user questions related to company policy, such as refund policy and company details.
    """
    # Initialize the FAISS index
    faiss_index = FAISS.load_local(folder_path='faiss_index', embeddings=None, allow_dangerous_deserialization=True)

    # Fetch the embedding for the query string
    query_embedding = await fetch_embedding(query_string)

    # Perform the similarity search using the computed embedding
    loop = asyncio.get_event_loop()
    docs = await loop.run_in_executor(executor, faiss_index.similarity_search_by_vector, query_embedding, 3)

    # Process the retrieved documents
    output = ""
    for doc in docs:
        output += " ".join(doc.page_content.split('\n'))
    
    return output
