import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

client = None
db = None
users_collection = None


def connect_to_mongo():
    global client, db, users_collection
    if client is None:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client["event_planner"]
        users_collection = db["users"]
        print("✅ Connected to MongoDB successfully!")
