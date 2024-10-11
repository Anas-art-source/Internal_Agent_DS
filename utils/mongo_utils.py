from pymongo import MongoClient, errors
from datetime import datetime
import os
from bs4 import BeautifulSoup

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDBManager:
    def __init__(self, db_name='internal_agent'):

        self.client = self._create_client()
        self.db_name = db_name
        self.db = None
        self.messages_collection = None

        self.connect_to_db()
    
    def _create_client(self):
        host = os.getenv('MONGODB_HOST', 'localhost:27017') 
        user = os.getenv('MONGODB_USER')
        password = os.getenv('MONGODB_PASS')
        
        if user and password:
            mongo_uri = f'mongodb://{user}:{password}@{host}/'
        else:
            mongo_uri = f'mongodb://{host}/'
        
        print(f"Connecting to MongoDB using URI: {mongo_uri}")
        return MongoClient(mongo_uri, retryWrites=False)

    def connect_to_db(self):
        self.db = self.client[self.db_name]
        self.messages_collection = self.db["messages"]

    def add_to_message(self, message_id, session_id, sender, name, content, email, product_list=None, filename=None, is_html=False, chart_data=None, cost=0):
        logger.info(f"Mongo > storing messages in session_id: {session_id} and message_id: {message_id}")
        message_entry = {
            'message_id': message_id,
            'sender': sender,
            'name': name,
            'content': content,
            'session_id': session_id,
            'email': email,
            'product_list': product_list if product_list else [],
            'chart_data': chart_data if chart_data else [],
            'filename': filename,
            'is_html': is_html,
            'timestamp': datetime.utcnow(),
            'cost': cost
        }
        self.messages_collection.insert_one(message_entry)

    def get_conversation_history(self, session_id):
        conversation = self.messages_collection.find({"session_id": session_id}).sort("timestamp", 1)
        conversation_list = []

        for message in conversation:
            content = message['content']
            
            if message.get('is_html', False):
                soup = BeautifulSoup(content, 'html.parser')
                content = soup.get_text()

            if message.get('product_list'):
                content += ' ' + ' '.join(map(str, message['product_list']))
            if message.get('chart_data'):
                content += ' ' + ' '.join(map(str, message['chart_data']))
            
            conversation_list.append({
                'role': message['sender'],
                'content': content
            })

        return conversation_list
    
    def get_conversation_history_fe(self, session_id):
            conversation = self.messages_collection.find({"session_id": session_id}).sort("timestamp", 1)
            return conversation

    
    def flush_all_messages(self):
        self.messages_collection.delete_many({})

  

    def delete_collection(self, collection_name):
        if collection_name in self.db.list_collection_names():
            self.db.drop_collection(collection_name)
            print(f"Collection '{collection_name}' has been deleted.")
        else:
            print(f"Collection '{collection_name}' does not exist.")


mongodb_manager = MongoDBManager()












# mongodb_manager.delete_collection('logs')
# mongodb_manager.delete_collection('messages')


# # db_manager.connect_to_db()

# db_manager.add_to_log('session123', 'This is a log message.', 'user@example.com')

# db_manager.add_to_message(
#     session_id='session123',
#     sender='AI',
#     name='Fashion Assistant',
#     text='This is a sample message.',
#     email='user@example.com',
#     product_list=['product1', 'product2'],
#     filename='http://example.com/file.jpg'
# )
# Retrieve logs and messages
# logs = mongodb_manager.get_all_logs('e8Ln6JK5f7l3bQgdAAAF')
# messages = mongodb_manager.get_all_messages('e8Ln6JK5f7l3bQgdAAAF')

# print("Logs:", logs)
# print("Messages:", messages)

# db_manager.flush_all_logs()
# db_manager.flush_all_messages()

# # Retrieve logs and messages
# logs = db_manager.get_all_logs('session123')
# messages = db_manager.get_all_messages('session123')

# print("Logs2:", logs)
# print("Messages2:", messages)