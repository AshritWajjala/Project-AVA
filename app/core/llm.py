from app.core.config import settings
from app.core.prompts import SYSTEM_MODES
from app.core.security_utils import sanitize_user_input
from app.services.vector_engine import query_research
from app.core.llm_factory import get_llm_client
from app.database.mongodb import get_ava_context
from langchain_classic.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.logger import logger, log_error_cleanly

    
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
        context = get_ava_context("fitness") 
    elif mode_config["context_source"] == "journal_db":
        context = get_ava_context("journal")
    elif mode_config["context_source"] == "vector_store":
        context = query_research(question=safe_query)
    else:
        context="No specific data context needed."
        
    system_prompt = mode_config['instruction']
    
    logger.info("Retrieved context and system prompt")
    
    # 3. Check for "Empty Data" (Onboarding Logic)
    if not context:
        if "onboarding_ask" in mode_config:
            yield mode_config["onboarding_ask"]
            return
    

    
    user_message_format = """
    <CONTEXT>
    {context}
    </CONTEXT>
    
    USER QUESTION: {user_query}
    """
    
    # Creating prompt template
    prompt_template = ChatPromptTemplate.from_messages([
    ("system", "{system_instruction}"),
    ("user", user_message_format)
    ])
    logger.info("Created Prompt Template")
    
    # Defining LLM
    llm = get_llm_client(provider=provider, api_key=api_key)
    logger.info(f"LLM Defined: {llm}")
    
    # 4. Create the Chain
    chain = prompt_template | llm | StrOutputParser()
    
    try:
        # 1. Capture the stream
        for chunk in chain.stream(
                    {
                        "system_instruction": system_prompt,
                        "context": context,
                        "user_query": safe_query
                    }
                ):
            if chunk:
                yield chunk
            

    
    except Exception as e:
        yield f"⚠️ AVA Error: I encountered an issue processing that. ({str(e)})"