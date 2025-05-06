import pandas as pd
from dependency_injector.wiring import inject, Provide
from streamlit.errors import StreamlitSetPageConfigMustBeFirstCommandError

from components import iiif_viewer_component, header_component
import streamlit as st
from typing import Annotated, Dict, List

from container import AppContainer
from services import ManifestService


class ShowView:

    def __init__(self, manifest_service: ManifestService):
        self.manifest_service = manifest_service

    @staticmethod
    def page_header_render():
        header_component(title="IIIF Viewer", desc='Explore high-resolution images with the IIIF viewer')

    def render_iiif_viewer(self, manifest_url: str):

        if not manifest_url:
            manifest_url = 'https://inuyasha021.github.io/manifests/ff60c5db13074ecfb4cb5f3853373189/manifest.json'

        st.markdown("""
            <style>
            .element-container {
                margin-bottom: 0 !important;
            }
            .viewer-container {
                padding-top: 0;
                margin-top: 0;
            }
            .stHtmlContainer {
                margin-top: 0 !important;
                margin-bottom: 0 !important;
                padding-top: 0 !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Use a single container for the viewer
        with st.container():
            st.html('<div class="viewer-container">')
            iiif_viewer_component(manifest_url)
            st.html('</div>')

        meta_data: List[Dict[str, str]] = []
        manifest_entity = self.manifest_service.get_by_manifest_url(manifest_url)
        if manifest_entity:
            meta_data = manifest_entity.meta_data

        if meta_data:
            # 创建一个带有样式的卡片容器
            st.markdown("""
            <style>
            .metadata-card {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .metadata-item {
                display: flex;
                margin-bottom: 8px;
                align-items: baseline;
            }
            .metadata-key {
                font-weight: bold;
                min-width: 150px;
                color: #555;
            }
            .metadata-value {
                flex-grow: 1;
            }
            </style>
            """, unsafe_allow_html=True)

            # 使用HTML创建更美观的元数据显示
            metadata_html = '<div class="metadata-card">'
            for each in meta_data:
                metadata_html += f'<div class="metadata-item"><span class="metadata-key">{each["key"]}:</span> <span class="metadata-value">{each["value"]}</span></div>'
            metadata_html += '</div>'

            st.markdown(metadata_html, unsafe_allow_html=True)


    def render(self):
        try:
            st.set_page_config(
                page_title="IIIF Image Viewer",
                page_icon="🖼️",
                layout="wide"
            )
        except StreamlitSetPageConfigMustBeFirstCommandError:
            pass

        self.page_header_render()
        self.render_iiif_viewer(st.query_params.get('manifest_url', ''))


@inject
def show_view(manifest_service: Annotated[ManifestService, Provide[AppContainer.manifest_service]]):
    ShowView(manifest_service).render()


public_show_page = st.Page(show_view, url_path='show', title="IIIF Show", icon="🖼️")