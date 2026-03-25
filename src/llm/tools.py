from langchain_core.tools import tool
from src.database.mongodb import add_mongo_log
from src.services.vector_engine import query_research
from src.utils.logger import logger, log_error_cleanly
from langchain_groq import ChatGroq
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode
from config.config import settings
from langgraph.checkpoint.memory import MemorySaver
from datetime import datetime

# Import your models
from src.models.logs import FitnessLog, WorkoutLog, JournalLog

# 1. FITNESS TOOL
@tool(args_schema=FitnessLog)
def log_fitness_activity(weight: float = None, calories: int = None, protein: int = None):
    """
    Log health metrics (weight, calories, protein). 
    AVA: Use ONLY for EXPLICIT commands: 'log', 'save', 'record', or 'track'. 
    """
    try:
        # Pydantic validation
        data = FitnessLog(weight=weight, calories=calories, protein=protein)
        payload = data.model_dump()
        payload["timestamp"] = datetime.now()
        
        add_mongo_log(log_type="fitness", data_dict=payload)
        return f"Successfully recorded {weight}kg. Tracked for {settings.USER_NICKNAME}."
    except Exception as e:
        log_error_cleanly(e)
        return "Failed to save fitness entry."

# 2. WORKOUT TOOL - Fixed Signature
@tool(args_schema=WorkoutLog)
def log_workout_session(workout_type: str, exercises: list):
    """
    Saves a gym session. 
    AVA: 'exercises' MUST be a list of dicts with these EXACT keys:
    - 'exercise': (string) name of the movement
    - 'sets': (int) number of sets
    - 'reps': (int) number of reps
    - 'weight': (float) load used in kg
    """
    try:
        # Pack into Pydantic for strict validation before saving
        data = WorkoutLog(workout_type=workout_type, exercises=exercises)
        logger.info(f"Logging workout: {data.workout_type}")
        
        payload = data.model_dump()
        payload["timestamp"] = datetime.now()
        
        add_mongo_log(log_type="workout", data_dict=payload)
        return f"Your {data.workout_type} workout has been logged."
    except Exception as e:
        log_error_cleanly(e)
        return f"Failed to save workout: {str(e)}"

# 3. JOURNAL TOOL - Fixed Signature
@tool(args_schema=JournalLog)
def save_journal_entry(content: str, mood: str, tags: list = []):
    """
    Saves a personal reflection or daily note. 
    AVA: Do NOT use a 'data' key. Provide content, mood, and tags as flat arguments.
    """
    try:
        # Pack into Pydantic
        data = JournalLog(content=content, mood=mood, tags=tags)
        logger.info(f"Saving journal entry for mood: {data.mood}")
        
        payload = data.model_dump()
        payload["timestamp"] = datetime.now()
        
        add_mongo_log(log_type="journal", data_dict=payload)
        return "Journal entry saved."
    except Exception as e:
        log_error_cleanly(e)
        return "Failed to save journal entry."

# 4. RESEARCH TOOL
@tool
def search_technical_docs(query: str):
    """
    Searches your local PDF library for AI, ML, or Programming answers.
    """
    # Assuming query_research is imported
    from src.services.vector_engine import query_research
    results = query_research(query)
    return f"Results from your technical library: {results}"

# --- GRAPH ORCHESTRATION ---

# Initialize Memory for Checkpointing
memory = MemorySaver()

# Initialize Groq
llm = ChatGroq(model="qwen/qwen3-32b", groq_api_key=settings.GROQ_API_KEY) 

tools = [log_fitness_activity, log_workout_session, save_journal_entry, search_technical_docs]

# Bind tools to the LLM
llm_with_tools = llm.bind_tools(tools)

# Define agent node
def call_model(state: MessagesState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# Build the Graph
builder = StateGraph(MessagesState)
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools)) # Prebuilt ToolNode handles schema mapping

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition) # Routes to tools or END
builder.add_edge("tools", "agent")

# Compile with INTERRUPT
# This triggers the 'state.next' pause in Streamlit
graph = builder.compile(checkpointer=memory, interrupt_before=["tools"])
# user_query = "I just finished a Push day. I did 3 sets of Flat Bench for 10 reps at 80kg and 3 sets of Overhead Press of 12 reps and lifted 2.5 kg as that was the maximum load I took take for my shoulders :|."
# inputs = {"messages": [("user", user_query)]}
# for chunk in graph.stream(inputs, stream_mode="values"):
#     chunk["messages"][-1].pretty_print()
    