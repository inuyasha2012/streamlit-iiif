import streamlit as st
from typing import Dict, Any

@st.cache_data
def get_auth_config() -> Dict[str, Any]:
    return st.secrets['auth'].to_dict()