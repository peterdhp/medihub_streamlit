import streamlit as st

def toggle_role():
    # This function toggles the role between 'patient' and 'doctor'
    if 'role' in st.session_state:
        if st.session_state.role == 'patient':
            st.session_state.role = 'doctor'
        else:
            st.session_state.role = 'patient'
    else:
        # Initialize the role if it's not set yet
        st.session_state.role = 'doctor'
        
