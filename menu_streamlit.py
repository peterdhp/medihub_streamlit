import streamlit as st
from utils_streamlit import *


if 'role' not in st.session_state :
    st.session_state.role = 'patient'

def authenticated_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("app_streamlit.py", label="질문하기")
    if st.session_state.status in ["text", "chat","response"]:
        if st.session_state.role in ['patient','admin'] :
            st.sidebar.page_link("pages/Q_helper_chat_number.py", label="질문 보완하기 (개수에 따라)")
            
    if st.session_state.status in ["text", "chat","response"]:
        if st.session_state.role in ['patient','admin'] :
            st.sidebar.page_link("pages/Q_helper_chat_stopToken.py", label="질문 보완하기 (stop token)")
    if st.session_state.status in ["text", "chat","response"]:
        if st.session_state.role in ['doctor','admin'] :
            st.sidebar.page_link("pages/A_helper.py", label="답변하기")
        
        
        #st.sidebar.page_link("pages/admin.py", label="Manage users")
        #st.sidebar.page_link("pages/super-admin.py",label="Manage admin access",disabled=st.session_state.role != "super-admin",)


def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("app_streamlit.py", label="질문하기")


def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu
    with st.sidebar:
        st.text('계정 모드')
        st.button(st.session_state.role, on_click=toggle_role)
        
    if "status" not in st.session_state or st.session_state.status is None:
        unauthenticated_menu()
        return
    authenticated_menu()


def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    
    #if "status" not in st.session_state or st.session_state.status is None:
        #st.switch_page("app_streamlit.py")
    menu()