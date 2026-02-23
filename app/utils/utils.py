import streamlit as st
  
    
def add_exercise():
    if "workout" not in st.session_state:
        st.session_state.workout_list = []
        
    st.session_state.workout_list.append({
        "log_date": st.session_state.wk_date,
        "workout_type": st.session_state.wk_type,
        "exercise": st.session_state.exercise_name,
        "sets": st.session_state.s,
        "reps": st.session_state.r,
        "load": st.session_state.w
    })
