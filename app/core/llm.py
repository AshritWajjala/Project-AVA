from app.core.config import settings
from app.core.prompts import SYSTEM_MODES
from app.core.security_utils import sanitize_user_input
from app.services.vector_engine import query_research
from app.core.llm_factory import get_llm_client
from app.database.mongodb import get_ava_context,save_chat_to_mongo
from langchain_classic.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.logger import logger, log_error_cleanly

    
def get_ava_response(mode, user_input, session_id, session_title, provider, api_key):
    """
    Main entry point for AVA logic. Handles routing, context fetching, 
    and generating response.
    """
    
    # 1. Sanitize the Input (Safety Layer)
    safe_query = sanitize_user_input(user_input)
    if "bypass my core safety" in safe_query:
        return safe_query
    
    # Logs User Query
    save_chat_to_mongo(session_id, session_title, "user", safe_query)

    # 2. Dynamic Context Fetching (Routing)
    # We fetch data only relevant to the current mode to save tokens and improve accuracy
    context = ""
    mode_config = SYSTEM_MODES[mode]
    
    if mode_config["context_source"] == "fitness_db":
        context = get_ava_context("fitness") 
    elif mode_config["context_source"] == "journal_db":
        context = get_ava_context("journal")
    elif mode_config["context_source"] == "vector_store":
        search_results = query_research(question=safe_query)
        if search_results and "No relevant info found" not in search_results:
            context = search_results
        else:
            context = "No specific document context found for this query."
    else:
        context="No specific data context needed."
        
        
    system_prompt = mode_config['instruction']
    
    logger.info("Retrieved context and system prompt")
    
    # 3. Check for "Empty Data" (Onboarding Logic)
    if context and len(context.strip()) > 50:
        user_message_format = """
        <CONTEXT>
        {context}
        </CONTEXT>
        
        USER QUESTION: {user_query}
        """
    else:
        # No context available or relevant -> Send only the query
        user_message_format = "{user_query}"
        context = "" # Ensure it's empty for the chain.invoke call
    
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
        full_response = ""
        for chunk in chain.stream(
                    {
                        "system_instruction": system_prompt,
                        "context": context,
                        "user_query": safe_query
                    }
                ):
            if chunk:
                full_response += chunk
                yield chunk
        
        # Logging Assistant response
        save_chat_to_mongo(session_id=session_id, 
                           session_title=session_title, 
                           role="assistant",
                           content=full_response)
    
    except Exception as e:
        yield f"⚠️ AVA Error: I encountered an issue processing that. ({str(e)})"
        
def get_chat_title(first_query):
    """Generates a title for the conversation based on user's first query

    Args:
        first_query (str): User's first query.
    """
    try:
        llm = get_llm_client(provider="Ollama (Local)")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a specialized summarizer. Create a 3-word title for the user's chat. Return ONLY the title words. No quotes, no intro."),
            ("user", "{query}")
        ])
        
        chain = prompt | llm | StrOutputParser()
        
        return chain.invoke({"query": first_query}).strip()
        
    except Exception as e:
        logger.warning("Error genrating chat title. Proceeding with first 25 characters. \nError: {e} ")
        # To continue application smoothly
        return first_query[:25] + '...'