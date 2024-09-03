# history_service.py

from pymongo import MongoClient
from datetime import datetime

class HistoryService:
    def __init__(self, db_url):
        self.client = MongoClient(db_url)
        self.db = self.client.chatbot
        self.collection = self.db.history

    def save_history(self, user_id, question, answer):
        self.collection.insert_one({
            'user_id': user_id,
            'question': question,
            'answer': answer,
            'timestamp': datetime.now()
        })

    def get_history(self, user_id):
        return list(self.collection.find({'user_id': user_id}).sort("timestamp", -1))

    def clear_history(self, user_id):
        self.collection.delete_many({'user_id': user_id})
