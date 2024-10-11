# from pymongo import MongoClient
# from pymongo.collection import Collection


# class MongoDBManager:
#     def __init__(self, db_url: str, db_name: str):
#         self.client = MongoClient(db_url)
#         self.db = self.client[db_name]

#     def insert_document(self, collection_name: str, data: dict) -> str:
#         collection: Collection = self.db[collection_name]
#         result = collection.insert_one(data)
#         return str(result.inserted_id)

#     def find_documents(self, collection_name: str, query: dict) -> list:
#         collection: Collection = self.db[collection_name]
#         return list(collection.find(query))

#     def update_document(self, collection_name: str, query: dict, new_values: dict) -> int:
#         collection: Collection = self.db[collection_name]
#         result = collection.update_many(query, {'$set': new_values})
#         return result.modified_count

#     def delete_document(self, collection_name: str, query: dict) -> int:
#         collection: Collection = self.db[collection_name]
#         result = collection.delete_many(query)
#         return result.deleted_count


# mongoDBManager = MongoDBManager(
#     db_name='internal_agent_logs',
#     db_url='mongodb://root:gF4XVjcGsw@logs-mongodb.common.svc.cluster.local:27017/'
# )
