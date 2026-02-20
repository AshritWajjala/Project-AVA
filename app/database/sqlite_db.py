from app.core.config import settings
import sqlite3
from app.core.logger import logger, log_error_cleanly
from app.core.exceptions import *

# Connect (creates the file if it doesn't exists)
def init_fitness_db():
    try:
        # The 'with' statement handles closing the connection automatically
        with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
            cursor = conn.cursor()
            logger.info("Established Connection to fitness database.")
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS fitness_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,  
            weight REAL NOT NULL,
            calories INTEGER NOT NULL,
            protein REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,  
            workout_type TEXT NOT NULL,
            exercise_name TEXT NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight_lifted REAL NOT NULL,
            rpe INTEGER,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Commit is still needed to save changes
            conn.commit()
            logger.info("Tables verified/created in SQLite.")

    except Exception as e:
        log_error_cleanly(e)
        raise DatabaseException("Database Initialization Failed")

def add_fitness_log(date, weight, calories, protein, notes=None):
    try:
            with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
                cursor = conn.cursor()
                logger.info("Adding Fitness Log: Initiated.")
                
                query = """
                INSERT INTO fitness_logs (date, weight, calories, protein, notes)
                VALUES (?, ?, ?, ?, ?)
                """
                
                cursor.execute(query, (date, weight, calories, protein, notes))
                
                # Commit is still needed to save changes
                conn.commit()
                logger.info("Adding Fitness Log: Completed.")

    except Exception as e:
        log_error_cleanly(e)
        raise DatabaseException("Failed to add fitness log")
    
def add_workout_log(date, workout_type, exercise_name, sets, reps, weight_lifted, rpe=None, metadata=None):
    try:
            with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
                cursor = conn.cursor()
                logger.info("Adding Workout Log: Initiated.")
                
                query = """
                INSERT INTO workout_logs (date, workout_type, exercise_name, sets, reps, weight_lifted,
                rpe, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """

                cursor.execute(query, (date, workout_type, exercise_name, sets, reps, weight_lifted,
                rpe, metadata))
                
                # Commit is still needed to save changes
                conn.commit()
                logger.info("Adding Workout Log: Completed.")

    except Exception as e:
        log_error_cleanly(e)
        raise DatabaseException("Failed to add workout log")
    
def get_fitness_history():
    try:
        with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
            # We use 'SELECT *' to get all columns
            query = "SELECT * FROM fitness_logs ORDER BY date DESC"
            import pandas as pd # Streamlit loves Pandas dataframes
            df = pd.read_sql_query(query, conn)
            return df
    except Exception as e:
        log_error_cleanly(e)
        return None

def get_workout_history():
    try:
        with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
            query = "SELECT * FROM workout_logs ORDER BY date DESC"
            import pandas as pd
            df = pd.read_sql_query(query, conn)
            return df
    except Exception as e:
        log_error_cleanly(e)
        return None
    
def clear_fitness_logs():
    try:
            with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
                cursor = conn.cursor()
                logger.info("Clearing Fitness Logs: Initiated.")
                
                query = """
                DELETE from fitness_logs
                """

                cursor.execute(query,)
                
                # Commit is still needed to save changes
                conn.commit()
                logger.info("Clearing Fitness Logs: Completed.")

    except Exception as e:
        log_error_cleanly(e)
        raise DatabaseException("Failed to clear fitness logs")    
    
def clear_workout_logs():
    try:
            with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
                cursor = conn.cursor()
                logger.info("Clearing Workout Logs: Initiated.")
                
                query = """
                DELETE from workout_logs
                """

                cursor.execute(query,)
                
                # Commit is still needed to save changes
                conn.commit()
                logger.info("Clearing Workout Logs: Completed.")

    except Exception as e:
        log_error_cleanly(e)
        raise DatabaseException("Failed to clear workout logs")    

def get_ai_context():
    context_parts = []
    
    with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
        cursor = conn.cursor()
        
        # 1. Fetch recent body stats
        cursor.execute("SELECT date, weight, calories FROM fitness_logs ORDER BY date DESC LIMIT 5")
        stats = cursor.fetchall()
        context_parts.append("Recent Body Stats:")
        for s in stats:
            context_parts.append(f"- {s[0]}: {s[1]}kg, {s[2]} kcal")

        # 2. Fetch recent workouts
        cursor.execute("SELECT date, workout_type, exercise_name, sets, reps, weight_lifted FROM workout_logs ORDER BY date DESC LIMIT 5")
        stats = cursor.fetchall()
        context_parts.append("Recent Workout Stats:")
        for s in stats:
            context_parts.append(f"- {s[0]}: {s[1]}, {s[2]}, {s[3]} sets, {s[4]} reps, {s[5]}kg")
        
    return "\n".join(context_parts)


init_fitness_db()
    
