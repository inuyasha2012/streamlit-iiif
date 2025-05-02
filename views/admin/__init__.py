import streamlit as st
from views.admin.image import image_view
from views.admin.manifest import manifest_view
from views.admin.embedding import embedding_view
from views.admin.annotation import anno_view

admin_image_page = st.Page(image_view, url_path='image',title='Image Management', icon='🖼️')
admin_manifest_page = st.Page(manifest_view, url_path='manifest', title='IIIF Manifests Management', icon='📚')
admin_embedding_page = st.Page(embedding_view, url_path='embedding', title='Embedding Management', icon='🔗')
admin_annotation_page = st.Page(anno_view, url_path='annotation', title='Annotation Management', icon='📝')

__all__ = ['admin_image_page', 'admin_manifest_page', 'admin_embedding_page', 'admin_annotation_page']