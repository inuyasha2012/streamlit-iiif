import streamlit as st
from views.auth import auth_login_page

def is_authenticated() -> bool:
    status = st.session_state.get('authentication_status', False)
    return status

def check_authentication() -> None:
    """Check if user is authenticated and provide a link to login if not"""
    if not is_authenticated():
        st.warning("Please log in to access this page")
        if st.button("Go to login page"):
            st.switch_page(auth_login_page)
        st.stop()
