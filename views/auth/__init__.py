import streamlit as st
from views.auth.login import login_view
from views.auth.logout import logout_view

auth_login_page = st.Page(login_view, url_path='login', title="Login", icon="🔑")
auth_logout_page = st.Page(logout_view, url_path='logout', title="Logout", icon="🔑")

__all__ = ["auth_login_page", "auth_logout_page"]