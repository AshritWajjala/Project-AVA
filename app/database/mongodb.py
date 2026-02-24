import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, UTC
from app.core.config import settings

# 1. Initialization
# Using the URI structure you just verified
uri = f"mongodb+srv://{settings.MONGODB_USER_NAME}:{settings.MONGODB_PASSWORD}@project-ava-main.r0tq155.mongodb.net/?appName=project-ava-main"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["ProjectAVA"]
logs_collection = db["life_logs"]

# 2. The Universal Logging Function
def add_mongo_log(log_type, data_dict):
    """
    Saves any data (Fitness, Workout, Journal) to MongoDB.
    'log_type' should be: 'fitness', 'workout', or 'journal'
    """
    document = {
        "user_nickname": settings.USER_NICKNAME,
        "type": log_type,
        "timestamp": datetime.now(UTC),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "payload": data_dict # This stores the specific fields (weight, reps, etc.)
    }
    
    try:
        result = logs_collection.insert_one(document)
        return result.inserted_id
    except Exception as e:
        print(f"❌ MongoDB Insert Error: {e}")
        return None

# 3. Helper for fetching history (for your graphs)
def get_mongo_history(log_type, limit=30):
    cursor = logs_collection.find({"type": log_type}).sort("timestamp", -1).limit(limit)
    return list(cursor)

def get_ava_context(log_type, limit=5):
    logs = get_mongo_history(log_type=log_type, limit=limit)
    
    if not logs:
        return f"No recent {log_type} records found."
    
    context_lines = []
    for log in logs:
        date = log.get("date", "Unknown Date")
        payload = log.get("payload", {})
        context_lines.append(f"- [{date}]: {payload}")
        
    return "\n".join(context_lines)


    