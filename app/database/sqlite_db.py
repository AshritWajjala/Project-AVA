import sqlite3
import pandas as pd
from datetime import datetime
from app.core.config import settings
from app.core.logger import logger, log_error_cleanly
from app.core.exceptions import DatabaseException

# --- INITIALIZATION ---
def init_db():
    """Verifies and creates all tables required for the modular Life OS."""
    try:
        with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
            cursor = conn.cursor()
            
            # 1. Body Stats & Nutrition
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS fitness_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,  
                weight REAL NOT NULL,
                calories INTEGER NOT NULL,
                protein REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")

            # 2. Gym Performance (PPL)
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
            )""")

            # 3. Personal Reflections (Journaling)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                content TEXT NOT NULL,
                mood TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")
            
            conn.commit()
            logger.info("Database initialized: All tables verified.")
    except Exception as e:
        log_error_cleanly(e)
        raise DatabaseException("Database Initialization Failed")

# --- FITNESS & DIET DATA METHODS ---
def add_fitness_log(date, weight, calories, protein, notes=None):
    try:
        with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
            cursor = conn.cursor()
            query = "INSERT INTO fitness_logs (date, weight, calories, protein, notes) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(query, (date, weight, calories, protein, notes))
            conn.commit()
    except Exception as e:
        log_error_cleanly(e)
        raise DatabaseException("Failed to add fitness log")

def add_workout_log(date, workout_type, exercise_name, sets, reps, weight_lifted, rpe=None, metadata=None):
    try:
        with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
            cursor = conn.cursor()
            query = """INSERT INTO workout_logs (date, workout_type, exercise_name, sets, reps, weight_lifted, rpe, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            cursor.execute(query, (date, workout_type, exercise_name, sets, reps, weight_lifted, rpe, metadata))
            conn.commit()
    except Exception as e:
        log_error_cleanly(e)
        raise DatabaseException("Failed to add workout log")

def get_fitness_history():
    try:
        with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
            return pd.read_sql_query("SELECT * FROM fitness_logs ORDER BY date DESC", conn)
    except Exception as e:
        log_error_cleanly(e)
        return pd.DataFrame()

def get_workout_history():
    try:
        with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
            return pd.read_sql_query("SELECT * FROM workout_logs ORDER BY date DESC", conn)
    except Exception as e:
        log_error_cleanly(e)
        return pd.DataFrame()

# --- JOURNALING METHODS ---
def add_journal_entry(content, mood="Neutral", tags=""):
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
            cursor = conn.cursor()
            query = "INSERT INTO journal_entries (date, content, mood, tags) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (today, content, mood, tags))
            conn.commit()
    except Exception as e:
        log_error_cleanly(e)
        raise DatabaseException("Failed to save journal entry")

# --- MODULAR AI CONTEXT FETCHERS ---
# These supply the 'Brain' with specific data depending on the selected mode

def get_fitness_context():
    """Builds a string of recent physical activity and nutrition."""
    try:
        with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
            cursor = conn.cursor()
            context = "### RECENT BODY STATS (Date, Weight, Cals):\n"
            cursor.execute("SELECT date, weight, calories FROM fitness_logs ORDER BY date DESC LIMIT 5")
            for row in cursor.fetchall():
                context += f"- {row[0]}: {row[1]}kg, {row[2]} kcal\n"
            
            context += "\n### RECENT WORKOUTS (Date, Exercise, Load):\n"
            cursor.execute("SELECT date, exercise_name, sets, reps, weight_lifted FROM workout_logs ORDER BY date DESC LIMIT 5")
            for row in cursor.fetchall():
                context += f"- {row[0]}: {row[1]} ({row[2]}x{row[3]} @ {row[4]}kg)\n"
            return context
    except Exception:
        return ""

def get_journal_context():
    """Builds a string of recent mental/emotional reflections."""
    try:
        with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
            cursor = conn.cursor()
            context = "### RECENT JOURNAL ENTRIES:\n"
            cursor.execute("SELECT date, content, mood FROM journal_entries ORDER BY date DESC LIMIT 5")
            for row in cursor.fetchall():
                context += f"- {row[0]} [Mood: {row[2]}]: {row[1]}\n"
            return context
    except Exception:
        return ""

# --- MAINTENANCE ---
def clear_fitness_logs():
    with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
        conn.execute("DELETE FROM fitness_logs")
        conn.commit()

def clear_workout_logs():
    with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
        conn.execute("DELETE FROM workout_logs")
        conn.commit()

def clear_journal_entries():
    with sqlite3.connect(settings.SQLITE_DB_PATH) as conn:
        conn.execute("DELETE FROM journal_entries")
        conn.commit()     


# --- AUTO-INIT ---
init_db()