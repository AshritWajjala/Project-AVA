import streamlit as st
from datetime import date
import os
import uuid
from src.database.mongodb import add_mongo_log, get_unique_sessions, get_session_messages, save_chat_to_mongo
from src.utils.utils import *
from src.llm.llm import get_chat_title
from config.config import settings
from src.services.vector_engine import index_pdf, clear_research_collection

from src.utils.logger import logger, log_error_cleanly
from src.utils.llm_utils import convert_messages, validate_api_key
from langchain_core.messages import AIMessage

# MUST BE FIRST
st.set_page_config(page_title="AVA: Life OS", layout="wide", page_icon="🛡️")

# --- INITIALIZATION ---
if "api_validated" not in st.session_state:
    st.session_state.api_validated = False
if "initialized_log_done" not in st.session_state:
    logger.info("Initiated AVA - Fresh Session")
    st.session_state.initialized_log_done = True

# Standard Session State Defaults
state_defaults = {
    "exercise_count": 1, 
    "messages": [], 
    "fit_weight": float(settings.CURRENT_WEIGHT),
    "fit_cals": int(settings.DAILY_CALORIE_GOAL), 
    "fit_prot": 0,
    "current_session_id": str(uuid.uuid4()), 
    "current_session_title": "New Conversation",
    "pending_log": None, 
    "show_confirmation": False
}

for key, val in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- SIDEBAR: NAVIGATION & CONFIG ---
st.sidebar.title("🛡️ Project AVA")
st.sidebar.divider()

app_mode = st.sidebar.radio("Navigation", ["Dashboard", "AI Sidekick"])

if app_mode == "AI Sidekick":
    st.sidebar.success("🛡️ **AVA Core Active**")
    
    # --- GATEKEEPER: BRAIN CONFIGURATION ---
    st.sidebar.divider()
    st.sidebar.subheader("🧠 Brain Configuration")
    
    if not st.session_state.api_validated:
        p_options = ["Groq", "OpenAI", "Gemini 3 Flash"]
        if settings.ENABLE_LOCAL_LLM: 
            p_options.append("Ollama (Local)")
        
        sel_prov = st.sidebar.selectbox("LLM Provider", options=p_options)
        
        if sel_prov == "Ollama (Local)":
            if st.sidebar.button("Activate Local AVA"):
                st.session_state.api_validated = True
                st.session_state.provider = "Ollama (Local)"
                st.session_state.api_key = "local"
                st.rerun()
        else:
            temp_key = st.sidebar.text_input(f"Enter {sel_prov} API Key", type="password")
            if st.sidebar.button("Validate & Unlock"):
                with st.sidebar.status("Authenticating..."):
                    if validate_api_key(sel_prov, temp_key):
                        st.session_state.api_validated = True
                        st.session_state.api_key = temp_key
                        st.session_state.provider = sel_prov
                        st.rerun()
                    else:
                        st.sidebar.error("Invalid API Key. Connection failed.")
        
        # STOP UI RENDERING UNTIL VALIDATED
        st.info("🔑 **AI Activation Required**: Please provide a valid API key in the sidebar to access the Universal Agent.")
        st.stop() 
    
    else:
        st.sidebar.info(f"✅ Connected: **{st.session_state.provider}**")
        if st.sidebar.button("🔄 Reset Connection"):
            st.session_state.api_validated = False
            st.rerun()

    # --- KNOWLEDGE BASE (Unlocked) ---
    st.sidebar.divider()
    st.sidebar.subheader("📚 Knowledge Base")
    uploaded_research = st.sidebar.file_uploader("Upload Research PDF", type="pdf")
    if uploaded_research:
        temp_path = os.path.join("data", uploaded_research.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_research.getbuffer())
        if st.sidebar.button("Index Document"):
            with st.sidebar.status("Indexing... 🧠"):
                index_pdf(filepath=temp_path)
            st.sidebar.success(f"Indexed {uploaded_research.name}!") 
            os.remove(temp_path)
    
    # --- HISTORY (Unlocked) ---
    st.sidebar.divider()
    st.sidebar.subheader("📜 Recent History")
    past_sessions = get_unique_sessions()
    if not past_sessions:
        st.sidebar.caption("No past conversations found.")
    else:
        for sess in past_sessions:
            if st.sidebar.button(f"{sess['title']}", key=sess['_id']):
                st.session_state.current_session_id = sess['_id']
                st.session_state.current_session_title = sess['title']
                st.session_state.messages = get_session_messages(session_id=sess['_id'])
                st.rerun()

    if st.sidebar.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_session_title = "New Conversation"
        st.session_state.current_session_id = str(uuid.uuid4())
        st.rerun()

st.sidebar.divider()
st.sidebar.caption(f"v0.5.0-ALPHA | Dev: {settings.USER_NICKNAME}")

# --- DASHBOARD CALLBACKS ---
def save_fitness_callback():
    w = st.session_state.get("fit_weight", 0.0)
    if w > 0:
        payload = {
            "weight": w, 
            "calories": st.session_state.get("fit_cals", 0), 
            "protein": st.session_state.get("fit_prot", 0)
        }
        add_mongo_log("fitness", payload) 
        st.toast(f"Fitness Log Saved! (Current: {w}kg)")
    else:
        st.error("Invalid weight.")

def save_workout_callback():
    exercises = []
    for i in range(st.session_state.exercise_count):
        name = st.session_state.get(f"ex_name_{i}")
        if name:
            exercises.append({
                "exercise": name, 
                "sets": st.session_state.get(f"sets_{i}", 1), 
                "reps": st.session_state.get(f"reps_{i}", 1), 
                "weight": st.session_state.get(f"load_{i}", 0.0)
            })
    if exercises:
        add_mongo_log("workout", {"split": st.session_state.wk_type, "exercises": exercises})
        st.session_state.exercise_count = 1
        st.toast("Workout logged to cloud! 💪")

# --- MAIN UI RENDERING ---
if app_mode == "Dashboard":
    st.title("🛡️ Project-AVA: Command Center")
    t1, t2, t3, t4, t5 = st.tabs(["📈 Fitness", "🏋️ Workouts", "📓 Journal", "📊 Analytics", "⚙️ Admin"])
    
    with t1:
        st.header("Body & Nutrition")
        st.number_input("Weight (kg)", step=0.1, key="fit_weight") 
        st.number_input("Calories (kcal)", step=50, key="fit_cals") 
        st.number_input("Protein (g)", step=5, key="fit_prot")
        st.button("Save Daily Stats", on_click=save_fitness_callback)

    with t2:
        st.header("Workout Logger")
        st.selectbox("Split", ["Push", "Pull", "Legs"], key="wk_type")
        for i in range(st.session_state.exercise_count):
            st.subheader(f"Exercise #{i+1}")
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            c1.text_input("Name", key=f"ex_name_{i}")
            c2.number_input("Sets", min_value=1, key=f"sets_{i}")
            c3.number_input("Reps", min_value=1, key=f"reps_{i}")
            c4.number_input("Weight (kg)", step=2.5, key=f"load_{i}")
        if st.button("➕ Add Exercise"):
            st.session_state.exercise_count += 1
            st.rerun()
        st.button("Log Entire Session", on_click=save_workout_callback)

    with t3:
        st.header("Daily Reflection")
        with st.form("journal_form", clear_on_submit=True):
            content = st.text_area("What's on your mind?")
            mood = st.select_slider("Mood", options=["Low", "Meh", "Neutral", "Good", "Great"], value="Neutral")
            tags = st.text_input("Tags (comma separated)")
            if st.form_submit_button("Log Entry"):
                if content:
                    add_mongo_log("journal", {"content": content, "mood": mood, "tags": tags.split(",")})
                    st.success("Reflection saved to MongoDB.")

    with t4:
        st.header("Progress Analytics")
        st.info("Visualizations (Plotly/Altair) will be integrated here in Phase 4.")

else: # AI SIDEKICK MODE
    st.title("🤖 AVA: Universal Agent")
    config = {"configurable": {"thread_id": st.session_state.current_session_id}}
    from src.llm.tools import graph

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # HITL Interrupt Logic (Confirmation UI)
    state = graph.get_state(config)
    if state.next:
        last_msg = state.values["messages"][-1]
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            with st.chat_message("assistant"):
                st.warning("🛡️ **AVA: Pending Confirmation**")
                st.json(last_msg.tool_calls[0]['args'])
                c1, c2 = st.columns(2)
                if c1.button("✅ Confirm & Save"):
                    for chunk in graph.stream(None, config, stream_mode="values"):
                        final_msg = chunk["messages"][-1]
                    st.session_state.messages.append({"role": "assistant", "content": final_msg.content})
                    save_chat_to_mongo(st.session_state.current_session_id, st.session_state.current_session_title, "assistant", final_msg.content)
                    st.rerun()
                if c2.button("❌ Cancel"):
                    cancel_msg = "Action cancelled by user."
                    graph.update_state(config, {"messages": [AIMessage(content=cancel_msg)]})
                    st.session_state.messages.append({"role": "assistant", "content": cancel_msg})
                    save_chat_to_mongo(st.session_state.current_session_id, st.session_state.current_session_title, "assistant", cancel_msg)
                    st.toast("Rejection logged.")
                    st.rerun()
        st.stop()

    # Chat Input
    if prompt := st.chat_input("Ask AVA to log something or research..."):
        if st.session_state.current_session_title == "New Conversation":
            st.session_state.current_session_title = get_chat_title(first_query=prompt)
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_chat_to_mongo(st.session_state.current_session_id, st.session_state.current_session_title, "user", prompt)
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            inputs = {"messages": convert_messages(st.session_state.messages)}
            full_res = ""
            container = st.empty()
            
            # Streaming Agent Response
            for chunk in graph.stream(inputs, config, stream_mode="updates"):
                if "agent" in chunk:
                    last_m = chunk["agent"]["messages"][-1]
                    if last_m.content:
                        full_res = last_m.content
                        container.markdown(full_res)
            
            # Finalize State
            if not graph.get_state(config).next:
                st.session_state.messages.append({"role": "assistant", "content": full_res})
                save_chat_to_mongo(st.session_state.current_session_id, st.session_state.current_session_title, "assistant", full_res)
            else:
                st.rerun()