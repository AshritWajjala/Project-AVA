from google.genai import types
from src.utils.logger import logger, log_error_cleanly

# For Google GenAI
# def get_safety_settings():
#     """
#     Returns high-threshold safety settings to prevent harmful content 
#     while allowing for fitness-related discussions.
#     """
#     return [
#         types.SafetySetting(
#             category="HARM_CATEGORY_DANGEROUS_CONTENT",
#             threshold="BLOCK_LOW_AND_ABOVE",  
#         ),
#         types.SafetySetting(
#             category="HARM_CATEGORY_HARASSMENT",
#             threshold="BLOCK_MEDIUM_AND_ABOVE",
#         ),
#         types.SafetySetting(
#             category="HARM_CATEGORY_HATE_SPEECH",
#             threshold="BLOCK_ONLY_HIGH",
#         ),
#     ]
    
def sanitize_user_input(user_query: str) -> str:
    """
    Basic defense against prompt injection and toxic input.
    """
    
    try:    
        # 1. Strip whitespace and limit length to prevent 'buffer overflow' style prompt attacks
        sanitized = user_query.strip()[:1000]

        # 2. Block common jailbreak keywords
        forbidden_terms = ["ignore all previous", "system prompt", "developer mode"]
        for term in forbidden_terms:
            if term in sanitized.lower():
                logger.warning(f"SECURITY ALERT: Potential prompt injection detected! Term: '{term}'")
                return "I am sorry, but I cannot fulfill requests to bypass my core safety instructions."
        
        # Log successful sanitization for debugging long inputs
        if len(user_query) > 1000:
            logger.info(f"Input truncated from {len(user_query)} to 1000 characters.")
            
        return sanitized
        
    except Exception as e:
        log_error_cleanly(e)
        return "I encountered an error processing your message safely."  
