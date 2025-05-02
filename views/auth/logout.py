import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os


def logout_view():
    st.set_page_config(
        page_title="IIIF Manifests",
        page_icon="📚",
        layout="wide"
    )

    # Load configuration file with users credentials
    config_path = 'config.yaml'
    if os.path.exists(config_path):
        with open(config_path) as file:
            config = yaml.load(file, Loader=SafeLoader)
    else:
        # Default config if file doesn't exist
        config = {
            'credentials': {
                'usernames': {
                    'admin': {
                        'name': 'admin',
                        'password': stauth.Hasher().hash('admin')
                    }
                }
            },
            'cookie': {
                'name': 'manifest_auth',
                'key': 'some_signature_key',
                'expiry_days': 30
            }
        }
        with open(config_path, 'w') as file:
            yaml.dump(config, file)

    # Create authenticator
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    if st.session_state.get('authentication_status'):
        authenticator.logout()
