from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
import streamlit as st
from app.core.config import settings


@st.cache_resource
def get_llm_client(provider, api_key):
    if provider == "Ollama (Local)": 
        return ChatOllama(model=settings.OLLAMA_MODEL_NAME, temperature=0)
        
    if provider == "Groq": 
        return ChatGroq(model=settings.GROQ_MODEL_NAME, temperature=0, api_key=api_key)
        
    if provider == "OpenAI": 
        return ChatOpenAI(model=settings.OPENAI_MODEL_NAME, temperature=0, api_key=api_key)
        
    if provider == "Gemini 3 Flash": 
        return ChatGoogleGenerativeAI(model=settings.GOOGLE_GENAI_MODEL_NAME, temperature=0, api_key=api_key)
    
    return None

