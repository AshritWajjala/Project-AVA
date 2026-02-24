import streamlit as st
from datetime import date
import os
# from app.database.sqlite_db import *
from app.database.mongodb import add_mongo_log
from app.utils.utils import *
from app.core.llm import get_ava_response
from app.core.prompts import SYSTEM_MODES
from app.core.config import settings
from app.services.vector_engine import index_pdf, clear_research_collection

from app.core.logger import logger, log_error_cleanly


# MUST BE FIRST
st.set_page_config(page_title="AVA: Life OS", layout="wide", page_icon="🛡️")
logger.info("Initiated AVA")

# --- INITIALIZATION ---
if "exercise_count" not in st.session_state:
    st.session_state.exercise_count = 1
if "messages" not in st.session_state:
    st.session_state.messages = []
if "fit_weight" not in st.session_state:
    st.session_state["fit_weight"] = float(settings.CURRENT_WEIGHT)
if "fit_cals" not in st.session_state:
    st.session_state["fit_cals"] = int(settings.DAILY_CALORIE_GOAL)
if "fit_prot" not in st.session_state:
    st.session_state["fit_prot"] = 0

logger.info("Defined all session state variables.")

# --- SIDEBAR: MODE SELECTOR & CONFIG ---
st.sidebar.title("🛡️ Project AVA")
st.sidebar.divider()

app_mode = st.sidebar.radio("Navigation", ["Dashboard", "AI Sidekick"])

# Logic for AI Sidekick Configuration
if app_mode == "AI Sidekick":
    selected_ai_mode = st.sidebar.selectbox(
        "Select Intelligence Mode",
        options=list(SYSTEM_MODES.keys()),
        help="Switches AVA's system prompt and data context."
    )
    
    # --- RESEARCH MODE UI ---
    if selected_ai_mode == "Research Mode":
        logger.info("Selected Research mode.")
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
                st.sidebar.success(f"Successfully indexed {uploaded_research.name}!") 
                os.remove(temp_path)
            if st.sidebar.button("🗑️ Clear Knowledge Base"):
                msg = clear_research_collection()
                st.sidebar.warning(msg)
                
    # --- BRAIN CONFIGURATION ---
    st.sidebar.divider()
    st.sidebar.subheader("🧠 Brain Configuration")
    
    selected_provider = st.sidebar.selectbox(
        "LLM Provider",
        options=["Ollama (Local)", "Gemini 3 Flash", "Groq", "OpenAI"],
        index=0
    )
    
    # Conditional API Key Entry
    api_key = None
    if selected_provider != "Ollama (Local)":
        api_key = st.sidebar.text_input(
            f"Enter {selected_provider} API Key",
            type="password",
            help=f"Required for {selected_provider} inference."
        )
        if not api_key:
            st.sidebar.warning(f"⚠️ API key required for {selected_provider}")

    # Store configurations in session state
    st.session_state.provider = selected_provider
    st.session_state.api_key = api_key
    
    st.sidebar.divider()
    if st.sidebar.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

st.sidebar.divider()
st.sidebar.caption(f"v0.5.0-ALPHA | Dev: {settings.USER_NICKNAME}")

# --- CALLBACK FUNCTIONS ---
def save_workout_callback():
    exercises = []
    for i in range(st.session_state.exercise_count):
        name = st.session_state.get(f"ex_name_{i}")
        if name and name.strip():
            exercises.append({
                "exercise": name,
                "sets": st.session_state.get(f"sets_{i}", 1),
                "reps": st.session_state.get(f"reps_{i}", 1),
                "weight": st.session_state.get(f"load_{i}", 0.0)
            })

    if exercises:
        payload = {
            "split": st.session_state.wk_type,
            "exercises": exercises
        }
        # Save to MongoDB
        add_mongo_log("workout", payload)
        
        # Reset UI state
        for i in range(st.session_state.exercise_count):
            st.session_state[f"ex_name_{i}"] = ""
        st.session_state.exercise_count = 1
        st.toast("Workout session saved to Cloud! 💪")
    
def save_fitness_callback():
    w = st.session_state.get("fit_weight", 0.0)
    if w > 0:
        payload = {
            "weight": w,
            "calories": st.session_state.get("fit_cals", 0),
            "protein": st.session_state.get("fit_prot", 0)
        }
        result = add_mongo_log("fitness", payload)
        print(f"DEBUG: Mongo Insert Result: {result}") # Check your VS Code terminal for this!
        st.toast(f"Fitness Log Saved! 📈")
    else:
        st.error("Weight must be greater than 0.")

# --- MAIN UI LOGIC ---
if app_mode == "Dashboard":
    st.title("🛡️ Project-AVA: Command Center")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Fitness", "🏋️ Workouts", "📓 Journal", "📊 Analytics", "⚙️ Admin"
    ])
    
    with tab1:
        st.header("Body & Nutrition")
        st.number_input("Weight (kg)", step=0.1, key="fit_weight") 
        st.number_input("Calories (kcal)", step=50, key="fit_cals") 
        st.number_input("Protein (g)", step=5, key="fit_prot")
        st.button("Save Daily Stats", on_click=save_fitness_callback)

    with tab2:
        st.header("Workout Logger")
        st.selectbox("Split", ["Push", "Pull", "Legs"], key="wk_type")
        for i in range(st.session_state.exercise_count):
            st.subheader(f"Exercise #{i+1}")
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            c1.text_input("Name", key=f"ex_name_{i}")
            c2.number_input("Sets", min_value=1, key=f"sets_{i}")
            c3.number_input("Reps", min_value=1, key=f"reps_{i}")
            c4.number_input("Weight (kg)", step=2.5, key=f"load_{i}")
            
        c1, c2 = st.columns(2)
        if c1.button("➕ Add Exercise"):
            st.session_state.exercise_count += 1
            st.rerun()
        if c2.button("➖ Remove Last"):
            if st.session_state.exercise_count > 1:
                st.session_state.exercise_count -= 1
                st.rerun()
        st.button("🚀 Log Entire Session", on_click=save_workout_callback, width="content")

    with tab3:
        st.header("Daily Reflection")
        with st.form("journal_form", clear_on_submit=True):
            content = st.text_area("What's on your mind?")
            mood = st.select_slider("Mood", options=["Low", "Meh", "Neutral", "Good", "Great"], value="Neutral")
            tags = st.text_input("Tags (comma separated)")
            if st.form_submit_button("Log Entry"):
                if content:
                    payload = {"content": content, "mood": mood, "tags": tags.split(",")}
                    add_mongo_log("journal", payload)
                    st.success("Reflection saved to MongoDB.")

    with tab4:
        st.header("Progress Analytics")
        st.info("Visualizations (Plotly/Altair) will be integrated here in Phase 4.")

    # with tab5:
    #     st.header("System Admin")
    #     st.warning("Danger Zone: These actions are irreversible.")
    #     if st.button("Clear Fitness Logs"):
    #         clear_fitness_logs() 
    #         st.toast("Fitness logs cleared! 👍")
    #     elif st.button("Clear Workout Logs"):
    #         clear_workout_logs()
    #         st.toast("Workout logs cleared! 👍")
    #     elif st.button("Clear Journal Entries"):
    #         clear_journal_entries()
    #         st.toast("Journal entries cleared! 👍")

else: # AI SIDEKICK MODE
    st.title(f"🤖 AVA: {selected_ai_mode}")
    
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Message AVA..."):
        # 1. Add user message to state and UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Generate Assistant Response
        with st.chat_message("assistant"):
            # Check for API Key requirement
            is_cloud = st.session_state.provider != "Ollama (Local)"
            if is_cloud and not st.session_state.api_key:
                st.error(f"Please enter your {st.session_state.provider} API Key in the sidebar.")
            else:
                try:
                    # Capture the stream
                    # We use a placeholder or a brief status for the initial connection
                    with st.spinner(f"Connecting to {st.session_state.provider}..."):
                        response_stream = get_ava_response(
                            mode=selected_ai_mode, 
                            user_input=prompt,
                            provider=st.session_state.provider,
                            api_key=st.session_state.api_key
                        )
                    
                    # STREAMING MAGIC: This iterates through the generator automatically
                    full_response = st.write_stream(response_stream)
                    
                    # 3. Store the final string in history
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                except Exception as e:
                    st.error(f"Error communicating with {st.session_state.provider}: {e}")