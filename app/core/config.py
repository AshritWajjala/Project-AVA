from pydantic_settings import BaseSettings, SettingsConfigDict

class MySettings(BaseSettings):
    SQLITE_DB_PATH: str 
    GROQ_API_KEY: str
    HF_TOKEN: str
    QDRANT_URL: str
    GEMINI_API_KEY: str
    
    model_config = SettingsConfigDict(env_file=".env")
    
settings = MySettings()
