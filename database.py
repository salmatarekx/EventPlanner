from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL", "mongodb://127.0.0.1:27017")

client = None
db = None
users_collection = None
events_collection = None
counters_collection = None

def connect_to_mongo():
    global client, db, users_collection, events_collection, counters_collection

    if client is None:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client["eventplanner"]   # same name as Compass database
        print("Connected to MongoDB successfully!")

    if db is not None:
        if users_collection is None:
            users_collection = db["users"]
        if events_collection is None:
            events_collection = db["events"]
        if counters_collection is None:
            counters_collection = db["counters"]
            # Initialize event counter if it doesn't exist
            if counters_collection.find_one({"_id": "event_id"}) is None:
                counters_collection.insert_one({"_id": "event_id", "sequence_value": 0})
                print("Initialized event ID counter")
