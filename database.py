import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import time

load_dotenv()
MONGO_URL = os.getenv("MONGO_URI", "mongodb://mongo-db:27017")

client = None
db = None
users_collection = None
events_collection = None
counters_collection = None

def connect_to_mongo(retries=10, delay=3):
    global client, db, users_collection, events_collection, counters_collection

    for attempt in range(retries):
        try:
            if client is None:
                client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
                db = client.get_database()
                print("Connected to MongoDB successfully!")

            if db is not None:
                if users_collection is None:
                    users_collection = db["users"]
                if events_collection is None:
                    events_collection = db["events"]
                if counters_collection is None:
                    counters_collection = db["counters"]
                    if counters_collection.find_one({"_id": "event_id"}) is None:
                        counters_collection.insert_one({"_id": "event_id", "sequence_value": 0})
                        print("Initialized event ID counter")
            return  # Success
        except ServerSelectionTimeoutError:
            print(f"MongoDB not ready, retrying in {delay}s... ({attempt+1}/{retries})")
            time.sleep(delay)

    raise Exception(f"Cannot connect to MongoDB after {retries} attempts")
