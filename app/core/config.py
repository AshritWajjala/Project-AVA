from pydantic_settings import BaseSettings, SettingsConfigDict

class MySettings(BaseSettings):
    SQLITE_DB_PATH: str 
    GROQ_API_KEY: str
    HF_TOKEN: str
    QDRANT_URL: str
    QDRANT_PATH: str
    GEMINI_API_KEY: str
    
    # Base Info
    USER_NAME: str
    USER_NICKNAME: str
    
    # Fitness specific
    DAILY_CALORIE_GOAL: int
    PROTEIN_GOAL: int
    CURRENT_WEIGHT: float
    TARGET_WEIGHT: float
    
    # MONGO_DB
    MONGODB_USER_NAME: str
    MONGODB_PASSWORD: str
    
    # models
    OLLAMA_MODEL_NAME: str
    OPENAI_MODEL_NAME: str
    GROQ_MODEL_NAME: str
    GOOGLE_GENAI_MODEL_NAME: str
    CHAT_TITLE_MODEL_NAME: str
    
    model_config = SettingsConfigDict(env_file=".env")
    
settings = MySettings()
