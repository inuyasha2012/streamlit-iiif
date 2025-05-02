from typing import Dict, List, Literal, TypeAlias, Tuple

import streamlit.components.v1 as components
import urllib.parse
import streamlit as st


def iiif_viewer_component(manifest_url: str):
    encoded_params = urllib.parse.urlencode({'iiif-content': manifest_url})
    return components.iframe(f"https://projectmirador.org/embed/?{encoded_params}", height=500)


def header_component(title: str, desc: str):
    html_header = f"""
          <style>
            .hero {{
                background: #f8f9fa;
                color: #212529;
                padding: 2rem 1.5rem;
                border-radius: 5px;
                text-align: center;
                margin-bottom: 1.5rem;
                border: 1px solid #dee2e6;
            }}
            .hero h1 {{
                font-size: 2.2rem;
                margin-bottom: 0.8rem;
                font-weight: 500;
            }}
            .hero p {{
                font-size: 1rem;
                max-width: 800px;
                margin: 0 auto;
                color: #6c757d;
            }}
          </style>
          <div class="hero">
            <h1>{title}</h1>
            <p>{desc}</p>
        </div>
    """
    st.html(html_header)

__all__ = ['iiif_viewer_component', 'header_component']
