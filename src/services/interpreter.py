from langchain_ollama import ChatOllama
from src.models.logs import FitnessLog, WorkoutLog, JournalLog
from config.config import settings
from src.utils.logger import logger, log_error_cleanly
from datetime import datetime


def get_structured_log(user_input: str, log_type: str):
    """Uses local LLM to transform chat into Pydantic object

    Args:
        user_input (str): The input provided by user.
        log_type (str): The type of the log.
    """
    try:
        logger.info(f"Starting structured extraction for type: {log_type}")
        
        # Setting up the local model
        llm = ChatOllama(model=settings.SMALL_OLLAMA_MODEL_NAME, temperature=0)
        
        # Map the log type to the correct Pydantic "form"
        schema_map = {
            "FITNESS": FitnessLog,
            "WORKOUT": WorkoutLog,
            "JOURNAL": JournalLog
        }
        
        selected_schema = schema_map.get(log_type)
        
        structured_llm = llm.with_structured_output(schema=selected_schema)
        
        result = structured_llm.invoke(user_input)
        
        logger.info(f"Sucessfully extracted {log_type} data.")
        
        return result

    except Exception as e:
        log_error_cleanly(e)
        return None
    
# result = get_structured_log(user_input="I weigh 110.6 kg today, also what's the latest on that QLoRA paper",
#                             log_type="FITNESS")
