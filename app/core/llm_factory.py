from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
import streamlit as st


@st.cache_resource
def get_llm_client(provider, api_key):
    if provider == "Ollama (Local)": 
        return ChatOllama(model="gemma3:27b", temperature=0)
        
    if provider == "Groq": 
        return ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=api_key)
        
    if provider == "OpenAI": 
        return ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
        
    if provider == "Gemini 3 Flash": 
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, api_key=api_key)
    
    return None

