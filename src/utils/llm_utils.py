from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
import streamlit as st
from config.config import settings
from src.utils.logger import logger, log_error_cleanly
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

def validate_api_key(provider, api_key):
    """
    Validates the API key by attempting a minimalist 1-token 
    invocation using LangChain.
    """
    logger.info(f"LangChain Handshake: Validating {provider}...")
    try:
        if provider == "Ollama (Local)":
            # For local, we assume the server is up on your Pop!_OS machine
            return True
            
        # 1. Initialize the specific LangChain client
        llm = get_llm_client(provider, api_key)
        
        if llm:
            # 2. Perform a "Connectivity Test" (1-token limit to save cost/time)
            # We use a simple HumanMessage to see if the API responds 200 OK.
            llm.invoke([HumanMessage(content="hi")], config={"max_tokens": 1})
            logger.info(f"{provider} validation successful.")
            return True
        
        return False
        
    except Exception as e:
        log_error_cleanly(e)
        # This catch will trigger if the API key is 401 Unauthorized or 403 Forbidden
        return False
    
    
@st.cache_resource
def get_llm_client(provider, api_key=None):
    """Returns LLM object.

    Args:
        provider (str): The name of the provider,
        api_key (str, optional): The api key (if paid version). Defaults to None.

    Returns:
        obj: LLM object
    """
    logger.info(f"Initializing LLM Client: {provider}")
    
    try:
        if provider == "Ollama (Local)": 
            logger.info(f"Connecting to local Ollama (Model: {settings.OLLAMA_MODEL_NAME})")
            return ChatOllama(model=settings.OLLAMA_MODEL_NAME, temperature=0)
            
        elif provider == "Groq":
            logger.info(f"Connecting to Groq (Model: {settings.GROQ_MODEL_NAME})") 
            return ChatGroq(model=settings.GROQ_MODEL_NAME, temperature=0, api_key=api_key)
            
        elif provider == "OpenAI": 
            logger.info(f"Connecting to OpenAI (Model: {settings.OPENAI_MODEL_NAME})")
            return ChatOpenAI(model=settings.OPENAI_MODEL_NAME, temperature=0, api_key=api_key)
            
        elif provider == "Gemini 3 Flash":
            logger.info(f"Connecting to Google Gemini (Model: {settings.GOOGLE_GENAI_MODEL_NAME})") 
            return ChatGoogleGenerativeAI(model=settings.GOOGLE_GENAI_MODEL_NAME, temperature=0, api_key=api_key)
        else:
            logger.warning(f"Unknown provider requested: {provider}")
            
        return None
    
    except Exception as e:
        log_error_cleanly(e)
        return None

def convert_messages(st_messages):
    """
    Converts Streamlit session_state dicts into LangChain Message objects.
    Ensures LangGraph can read the full conversation history.
    """
    converted = []
    for m in st_messages:
        role = m.get("role")
        content = m.get("content")
        
        if role == "user":
            converted.append(HumanMessage(content=content))
        elif role == "assistant":
            # If the message has tool_calls, you'd store them here in a real production app
            converted.append(AIMessage(content=content))
            
    return converted