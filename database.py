from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")

client = None
db = None
users_collection = None
events_collection = None


def connect_to_mongo():
    global client, db, users_collection, events_collection

    if client is None:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client["event_planner"]
        print("Connected to MongoDB successfully!")

    if db is not None:
        if users_collection is None:
            users_collection = db["users"]
        if events_collection is None:
            events_collection = db["events"]
