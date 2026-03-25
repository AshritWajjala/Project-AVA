import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, UTC
from config.config import settings
from src.utils.logger import logger, log_error_cleanly

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
    logger.info(f"Preparing to save {log_type} log to MongoDB Atlas...")
    
    document = {
        "user_nickname": settings.USER_NICKNAME,
        "type": log_type,
        "timestamp": datetime.now(UTC),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "payload": data_dict # This stores the specific fields (weight, reps, etc.)
    }
    
    try:
        result = logs_collection.insert_one(document)
        logger.info(f"Successful MongoDB Insert: {log_type} (ID: {result.inserted_id})")
    
        return result.inserted_id
    
    except Exception as e:
        log_error_cleanly(e)
        return None

# 3. Helper for fetching history (for your graphs)
def get_mongo_history(log_type, limit=30):
    f"""Retrieves the log history of type {log_type}

    Args:
        log_type (_type_): Type of the log
        limit (int, optional): Max number of logs retrieved. Defaults to 30.

    Returns:
        List: List of logs.
    """
    try:
        cursor = logs_collection.find({"type": log_type}).sort("timestamp", -1).limit(limit)
        return list(cursor)
    
    except Exception as e:
        log_error_cleanly(e)
        return []

def get_ava_context(log_type, limit=5):
    f"""Returns logs of type {log_type} for providing context to LLM.

    Args:
        log_type (str): The type of the log.
        limit (int, optional): Max number of logs retrieved. Defaults to 5.

    Returns:
        List: returns List(str) of logs.
    """
    logs = get_mongo_history(log_type=log_type, limit=limit)
    
    if not logs:
        return f"No recent {log_type} records found."
    
    try:
        context_lines = []
        for log in logs:
            date = log.get("date", "Unknown Date")
            payload = log.get("payload", {})
            context_lines.append(f"- [{date}]: {payload}")
            
        return "\n".join(context_lines)
    
    except Exception as e:
        log_error_cleanly(e)
        return []


def save_chat_to_mongo(session_id, session_title, role, content):
    """Logs individual messages to the chat_history collection.
    Args:
        session_id (_type_): ID of the session.
        session_title (_type_): Title of the session.
        role (_type_): Role of the message (User/AI/System).
        content (_type_): Content of the message.
    """
    try:
        chat_collection = db["chat_history"]
        chat_collection.insert_one(
            {
                "session_id": session_id,
                "session_title": session_title,
                "role": role,
                "content": content,
                "timestamp": datetime.now(UTC)
            }
        )
        
        logger.debug(f"Saved {role} message for session: {session_title}")
        
    except Exception as e:
        log_error_cleanly(e)
        
        

def get_unique_sessions():
    """Fetches all the unique session_id and titles for the streamlit sidebar
    """
    logger.info("Fetching session history from MongoDB...")
    
    try:
        chat_collection = db["chat_history"]
        pipeline = [
            {
                "$group": {
                    "_id": "$session_id",
                    "title": {"$first": "$session_title"},
                    "last_msg": {"$max": "$timestamp"}
                }
            },
            {"$sort": {"last_msg": -1}}
        ]
        
        sessions = list(chat_collection.aggregate(pipeline=pipeline))
        
        logger.info(f"Found {len(sessions)} unique chat sessions.")
        
        return sessions[:6]
    
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        return []
    
def get_session_messages(session_id):
    """Fetches all the messages for a specific session ID from the chat history.

    Args:
        session_id (str): ID of the session. 
    """
    try:
        chat_collection = db["chat_history"]
        session_messages = list(chat_collection.find({"session_id": session_id}).sort('timestamp', 1))
        logger.info(f"Retrieved {len(session_messages)} messages for session {session_id}")
        
        return session_messages
        
    except Exception as e:
        log_error_cleanly(e)
        return []