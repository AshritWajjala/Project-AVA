import streamlit as st
from datetime import date
from app.database.sqlite_db import *
from app.utils.utils import *

# MUST BE FIRST
st.set_page_config(page_title="AVA: Life OS", layout="wide")

# --- CALLBACK FUNCTIONS ---
def save_workout_callback():
    """Handles saving multiple exercises and resetting the form safely."""
    # 1. Loop through current exercise rows
    for i in range(st.session_state.exercise_count):
        name = st.session_state.get(f"ex_name_{i}")
        s = st.session_state.get(f"sets_{i}")
        r = st.session_state.get(f"reps_{i}")
        w = st.session_state.get(f"load_{i}")
        
        if name and name.strip(): # Only log if name is provided
            add_workout_log(
                date=str(st.session_state.wk_date),
                workout_type=st.session_state.wk_type,
                exercise_name=name,
                sets=s,
                reps=r,
                weight_lifted=w
            )
            
            # 2. SCRUB the keys (Safe inside a callback)
            st.session_state[f"ex_name_{i}"] = ""
            st.session_state[f"sets_{i}"] = 1
            st.session_state[f"reps_{i}"] = 1
            st.session_state[f"load_{i}"] = 0.0
    
    # 3. Reset the counter to start fresh next time
    st.session_state.exercise_count = 1
    st.toast("Workout session saved successfully! 💪")

# --- INITIALIZATION ---
st.title("🛡️ Project-AVA")

if "exercise_count" not in st.session_state:
    st.session_state.exercise_count = 1

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["Daily Stats", "Workout Log", "System Admin", "Progress Gallery"])

with tab1:
    st.header("📈 Body & Nutrition")
    log_date = st.date_input("Select Date", date.today(), key="fitness_date")
    
    # Defaulting to your starting weight and calorie targets
    weight = st.number_input("Weight (kg)", value=112.4, step=0.1) 
    calories = st.number_input("Calories (kcal)", value=2700, step=50) 
    protein = st.number_input("Protein (g)", value=0, step=5)

    if st.button("Save Daily Stats"):
        add_fitness_log(date=str(log_date), weight=weight, calories=calories, protein=protein)
        st.success(f"Log Saved for {log_date}!")

with tab2:
    st.header("🏋️ PPL Workout Logger")
    
    # Global Session Info - used by callback via session_state keys
    st.date_input("Date", date.today(), key="wk_date")
    st.selectbox("Split", ["Push", "Pull", "Legs"], key="wk_type")

    # The Dynamic Loop
    st.divider()
    for i in range(st.session_state.exercise_count):
        st.subheader(f"Exercise #{i+1}")
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        # Unique keys are vital for dynamic forms
        col1.text_input("Name", key=f"ex_name_{i}", placeholder="e.g. Bench Press")
        col2.number_input("Sets", min_value=1, key=f"sets_{i}")
        col3.number_input("Reps", min_value=1, key=f"reps_{i}")
        col4.number_input("Weight (kg)", step=2.5, key=f"load_{i}")
    
    st.divider()
    _, c1, _, c2, _ = st.columns([1, 1, 1, 1, 1])
    
    if c1.button("➕ Add Exercise"):
        st.session_state.exercise_count += 1
        st.rerun()
        
    if c2.button("➖ Remove Last"):
        if st.session_state.exercise_count > 1:
            st.session_state.exercise_count -= 1
            st.rerun()

    # The Final Submit - uses the callback pattern to avoid state lock
    st.button("🚀 Log Entire Session", on_click=save_workout_callback, use_container_width=True)

with tab3:
    st.header("⚙️ Database Management")
    if st.button("Clear Fitness Logs"):
        clear_fitness_logs()
        st.warning("All fitness data deleted.")
    
    if st.button("Clear Workout Logs"):
        clear_workout_logs()
        st.error("All workout data deleted.")

with tab4:
    st.header("📊 Your Transformation Journey")
    view_option = st.radio("View Data For:", ["Body Stats", "Gym Performance"], horizontal=True)
    
    if view_option == "Body Stats":
        data = get_fitness_history()
        if data is not None and not data.empty:
            st.subheader("Weight Trend")
            st.line_chart(data.set_index('date')['weight'])
            st.dataframe(data, use_container_width=True)
        else:
            st.info("No body stats logged yet. Start today!")
            
    else:
        data = get_workout_history()
        if data is not None and not data.empty:
            st.subheader("Lifting History")
            st.dataframe(data, use_container_width=True)
        else:
            st.info("No workouts logged yet. Time for a PPL session!")