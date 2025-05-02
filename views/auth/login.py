import streamlit as st
import streamlit_authenticator as stauth
from cache import get_auth_config
from views.public import public_home_page

def login_view():
    st.set_page_config(
        page_title="IIIF Manifests",
        page_icon="📚",
        layout="wide"
    )

    config = get_auth_config()

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # Add login widget
    authenticator.login(
        'main',
        2,
        max_login_attempts=3,  # Limit login attempts
        fields={'username': 'Email', 'password': 'Password'},  # Custom field labels
        captcha=False,  # Enable CAPTCHA
        clear_on_submit=True,  # Clear form on submit
        key='login_form'
    )

    if st.session_state.get('authentication_status'):
        st.switch_page(public_home_page)
    elif st.session_state.get('authentication_status') is False:
        st.error('Username/password is incorrect')
    elif st.session_state.get('authentication_status') is None:
        st.warning('Please enter your username and password')
