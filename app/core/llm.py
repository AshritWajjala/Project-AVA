from app.core.config import settings
from google import genai
from google.genai import types
from app.database.sqlite_db import get_fitness_context, get_journal_context
from app.core.prompts import SYSTEM_MODES
from app.core.security_utils import get_safety_settings, sanitize_user_input
from app.core.llm_factory import get_llm_client
from langchain_classic.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

    
def get_ava_response(mode, user_input, provider, api_key):
    """
    Main entry point for AVA logic. Handles routing, context fetching, 
    and generating response.
    """
    
    # 1. Sanitize the Input (Safety Layer)
    safe_query = sanitize_user_input(user_input)
    if "bypass my core safety" in safe_query:
        return safe_query

    # 2. Dynamic Context Fetching (Routing)
    # We fetch data only relevant to the current mode to save tokens and improve accuracy
    context = ""
    mode_config = SYSTEM_MODES[mode]
    
    if mode_config["context_source"] == "fitness_db":
        context = get_fitness_context() 
        system_prompt = mode_config['instruction']
    elif mode_config["context_source"] == "journal_db":
        context = get_journal_context()
        system_prompt = mode_config['instruction']
    elif mode_config["context_source"] == "vector_store":
        # Placeholder for Sunday's Vector/Research implementation
        context = "Reference the uploaded research documents and PDFs."
        system_prompt = mode_config['instruction']
    else:
        context="N/A"
        system_prompt = mode_config['instruction']
    
    # 3. Check for "Empty Data" (Onboarding Logic)
    if not context:
        if "onboarding_ask" in mode_config:
            yield mode_config["onboarding_ask"]
            return
    
    # 4. Create the Chain
    prompt_template = ChatPromptTemplate.from_messages([
    ("system", "{system_instruction}"),
    ("user", "CONTEXT FROM THE DATABASE: {user_context}\n\nUSER QUESTION: {user_query}")
    ])
    
    llm = get_llm_client(provider=provider, api_key=api_key)
    
    chain = prompt_template | llm |StrOutputParser()
    
    try:
        return chain.stream(
            {
                "system_instruction": system_prompt,
                "user_context": context if context else "No context needed.",
                "user_query": safe_query
            }
        )
    
    except Exception as e:
        return f"⚠️ AVA Error: I encountered an issue processing that. ({str(e)})"