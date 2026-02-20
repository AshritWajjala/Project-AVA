from app.core.config import settings
from google import genai
from google.genai import types
from app.database.sqlite_db import get_ai_context

def ava_gemini_response(user_query, context):
    # The client picks up the API key from settings
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    # Use the current 2026 stable preview
    model_id = 'gemini-3-flash-preview' 

    # We use the config object to provide system instructions
    config = types.GenerateContentConfig(
        system_instruction="You are AVA, Ashrit's fitness coach. Focus on his PPL routine and 85kg goal.",
        temperature=0,      # Zero for factual accuracy
        top_p=0.95,
        top_k=20
    )

    # Assemble the call
    response = client.models.generate_content(
        model=model_id,
        contents=f"CONTEXT FROM DATABASE:\n{context}\n\nUSER QUERY: {user_query}",
        config=config
    )
    
    return response

# Execution
user_query = "Hello :), give me a summary of the context you retrieved."
context = get_ai_context()

# Get response and print the text part
response = ava_gemini_response(user_query, context)
print(response.text)