from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from fastapi import FastAPI
import uvicorn
from langchain_ollama import ChatOllama
from langchain_classic.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from qdrant_client import QdrantClient

class State(TypedDict):
    query: str
    category: str
    response: str
    context: str

# LLM
specialist_llm = ChatOllama(model="gemma3:27b")
llm = ChatOllama(model="gemma3:4b")
parser = StrOutputParser()


# Helper Function
def generate_response(system_prompt,llm, state:State, clean=False):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{query}")
        ]
    )

    chain = prompt | llm | parser

    response = chain.invoke(
        {
            "query": state['query'],
            "context": state['context']
        }
    )
    if clean:
        return response.strip().lower()
    
    return response.strip()


# defining node methods
def memory_node_func(state:State):
    q_client = QdrantClient(url="http://127.0.0.1:6333")
    q_client.set_model("BAAI/bge-small-en-v1.5")
    
    # Searh for relevant docs
    results = q_client.query(
        collection_name="buddy_memories",
        query_text=state['query'],
        limit=3
    )

    relavant_memories = '\n'.join([result.document for result in results])
    
    return {"context": relavant_memories}

def router_node_func(state: State):
    system_prompt = """
    You are a routing assistant. Classify the following query into exactly one of these categories: [linux_mode, pc_mode].
    If neither of them, classify it as general.
    User Query: {query}
    """

    response = generate_response(system_prompt=system_prompt, state=state, llm=llm, clean=True)
    
    return {"category": response}

def linux_node_func(state: State):
    system_prompt = """
    You are a Linux expert. 
    Here is what you know about the user: {context}
    Answer the query for a linux enthusiast: {query}".
    """
    
    response = generate_response(system_prompt=system_prompt, state=state, llm=specialist_llm)
    
    return {"response": response}

def pc_node_func(state: State):
    system_prompt = """
    You are a PC hardware expert. 
    Here is what you know about the user: {context}
    Answer the query specifically for someone with a PC enthusiast: {query}
    """
    
    response = generate_response(system_prompt=system_prompt, state=state, llm=specialist_llm)
    
    return {"response": response}

def general_node_func(state: State):
    system_prompt = """
    You are a helpful and friendly assistant.
    Here is what you know about the user: {context}
    Please answer to the following User's query in less than 50 tokens.
    User Query: {query}
    """
    
    response = generate_response(system_prompt=system_prompt, state=state, llm=llm)
    
    return {"response": response}

def checking_category(state: State):
    valid_categories = ['pc_mode', 'linux_mode']
    category = state['category']
    if category in valid_categories:
        return category
    return "general"

# --- Graph Assembly ---
builder = StateGraph(State)

# Adding nodes
builder.add_node("memory_node", memory_node_func)
builder.add_node("router_node", router_node_func)
builder.add_node("linux_node", linux_node_func)
builder.add_node("pc_node", pc_node_func)
builder.add_node("general_node", general_node_func)

# Adding edges
builder.add_edge(START, "memory_node")
builder.add_edge("memory_node", "router_node")
builder.add_conditional_edges(
    "router_node",
    checking_category,
    {
        "linux_mode": "linux_node",
        "pc_mode": "pc_node",
        "general": "general_node"
    }
)

# Connecting nodes to the END
builder.add_edge("linux_node", END)
builder.add_edge("pc_node", END)
builder.add_edge("general_node", END)

# Compile and Run
buddy = builder.compile()

# Fast-API
app = FastAPI()




@app.get('/ask')
def func(q: str): # We take 'q' as a string from the URL
    # We build the 'Messenger Bag' (State) right here!
    input_state = {
        "query": q, 
        "category": "", 
        "response": ""
    }
    
    # Now we hand the bag to BUDDY
    result = buddy.invoke(input_state)
    
    return {
        "User Question": q,
        "BUDDY Decision": result['category'],
        "BUDDY Response": result['response']
    }
    
if __name__ == '__main__':
    uvicorn.run(app=app, host='localhost', port=8000)
    
