import logging
import sys
import traceback
from pathlib import Path
from datetime import datetime

# 1. Create the 'logs' directory if it doesn't exist
# This ensures the app doesn't crash because a folder is missing
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# 2. Generate a timestamped filename (e.g., ava_2026-02-20_10-30.log)
# This ensures that your files sort perfectly by date in your folder
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
LOG_FILE = LOG_DIR / f"{timestamp}.log"

# 1. Define how the text should look (Time - Name - Level - Message)
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 1. Terminal Handler (This shows text on your screen)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)

    # 2. File Handler (This actually CREATES the .log file and writes to it)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)

    return logger

# 3. Create a main logger for the app
logger = get_logger("AVA")

# 2. This is the "Magic Function" for clean errors
def log_error_cleanly(exception: Exception):
    """Prints only the important stuff when something breaks."""
    # Get the details of where the error happened
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    # Grab the very last part of the traceback (where your code failed)
    details = traceback.extract_tb(exc_traceback)[-1]
    file_name = details.filename.split("/")[-1] # Just the file name, not the whole path
    line_number = details.lineno
    
    # Print the clean version
    logger.error(f"❌ [Error Type]: {type(exception).__name__}")
    logger.error(f"📍 [Location]: File '{file_name}', Line {line_number}")
    logger.error(f"💬 [Message]: {str(exception)}")

