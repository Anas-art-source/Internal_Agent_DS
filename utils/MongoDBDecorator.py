import os
from functools import wraps
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError

class MongoDBDecorator:
    def __init__(self, db_name, collection_name):
        self.client = self._create_client()
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
    
    def _create_client(self):
        host = os.getenv('MONGODB_HOST', 'localhost:27017')
        user = os.getenv('MONGODB_USER')
        password = os.getenv('MONGODB_PASS')
        
        if user and password:
            mongo_uri = f'mongodb://{user}:{password}@{host}/'
        else:
            mongo_uri = f'mongodb://{host}/'
        
        print(f"Connecting to MongoDB using URI: {mongo_uri}")
        return AsyncIOMotorClient(mongo_uri)

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            tasks, values_to_store = result
            
            try:
                await self.collection.insert_one(values_to_store)
            except PyMongoError as e:
                print(f"Error inserting into MongoDB: {e}")
            
            print('here in decorator')
            return tasks
        
        return wrapper
    
async def sum_costs_by_message_id(message_id):
    host = os.getenv('MONGODB_HOST', 'localhost:27017')
    user = os.getenv('MONGODB_USER')
    password = os.getenv('MONGODB_PASS')
    
    if user and password:
        mongo_uri = f'mongodb://{user}:{password}@{host}/'
    else:
        mongo_uri = f'mongodb://{host}/'
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client['internal_agent']
    collection = db['logs']

    total_cost = 0.0
    async for log in collection.find({'message_id': message_id}):
        print("hereee!")
        total_cost += log.get('cost', 0.0)
    
    # await client.close()
    
    return total_cost
    


## OLD one
# from pymongo.errors import PyMongoError

# class MongoDBDecorator:
#     def __init__(self, db_name, collection_name):
#         self.client = self._create_client()
#         self.db = self.client[db_name]
#         self.collection = self.db[collection_name]
    
#     def _create_client(self):
#         host = os.getenv('MONGODB_HOST', 'localhost:27017')
#         user = os.getenv('MONGODB_USER')
#         password = os.getenv('MONGODB_PASS')
        
#         if user and password:
#             mongo_uri = f'mongodb://{user}:{password}@{host}/'
#         else:
#             mongo_uri = f'mongodb://{host}/'
        
#         print(f"Connecting to MongoDB using URI: {mongo_uri}")
#         return AsyncIOMotorClient(mongo_uri)

#     def __call__(self, func):
#         @wraps(func)
#         async def wrapper(*args, **kwargs):
#             result = await func(*args, **kwargs)
            
#             tasks, values_to_store = result
            
#             try:
#                 await self.collection.insert_one(values_to_store)
#             except PyMongoError as e:
#                 print(f"Error inserting into MongoDB: {e}")
            
#             print('here in decorator')
#             return tasks
        
#         return wrapper
