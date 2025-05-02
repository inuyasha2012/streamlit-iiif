from datetime import datetime, timedelta
from typing import TypedDict, Tuple, Annotated

import requests
import streamlit as st

import pandas as pd
from dependency_injector.wiring import Provide, inject
from streamlit.errors import StreamlitSetPageConfigMustBeFirstCommandError

from utils.iiif import IIIF3Image
from services import ImageService
from views.common.base import InterfaceCrudView
from helper.permission import check_authentication
from container import AppContainer


class ImageQueryDict(TypedDict):
    updated_at_start_date: str
    updated_at_end_date: str
    tag: str
    used: bool


class ImageView(InterfaceCrudView):

    def __init__(self, image_service: ImageService):
        self.image_service = image_service
        st.session_state.setdefault('selected_image_ids', [])
        st.session_state.setdefault('notification', {'type': None, 'message': None})

    def render_notification(self):
        notification = st.session_state.notification
        if notification.get('type', ''):
            getattr(st, notification.get('type', ''))(notification['message'])
            st.session_state.notification = {'type': None, 'message': None}

    def render_header_section(self):
        st.title("Image Management")

    def render_search_section(self) -> ImageQueryDict:
        with st.expander("Search Options", expanded=True):
            left, right = st.columns([1, 1])
            updated_at_start_date = left.date_input("updated After", value=datetime.now() - timedelta(days=30))
            updated_at_end_date = right.date_input("updated Before", value=datetime.now() + timedelta(days=1))
            tag = st.text_input("Tag")
            used = st.multiselect("Used", ["Yes", "No"], ["Yes", "No"])
            return {'updated_at_start_date': updated_at_start_date,
                    'updated_at_end_date': updated_at_end_date,
                    'tag': tag, 'used': used}

    def render_action_section(self) -> Tuple[bool, bool, bool, bool]:
        with st.sidebar:
            st.info("Select images to enable action buttons.")
            selected_ids = st.session_state['selected_image_ids']
            has_selections = bool(selected_ids)
            has_single_selection = len(selected_ids) == 1

            create_button = st.button("Create", use_container_width=True, disabled=has_selections)
            update_button = st.button("Update", use_container_width=True, disabled=not has_single_selection)
            delete_button = st.button("Delete", use_container_width=True, disabled=not has_selections)
            st.divider()
            create_manifest_button = st.button("Create Manifest", use_container_width=True, disabled=not has_selections)
        return create_button, update_button, delete_button, create_manifest_button

    def render_dataframe_section(self, query: ImageQueryDict):
        images = self.image_service.filter(**query)
        if not images:
            st.info("No images match your search criteria.")
            return

        df = pd.DataFrame([{
            "ID": img.id,
            "Thumbnail URL": img.thumbnail_url,
            "Info URL": img.info_url,
            "Used": img.used,
            "Tag": img.tag or '',
            "Created": img.created_at.strftime('%Y-%m-%d %H:%M'),
            "Updated": img.updated_at.strftime('%Y-%m-%d %H:%M') if img.updated_at else "",
        } for img in images])

        selection = st.dataframe(df, use_container_width=True, on_select="rerun",
                                 column_config={"Thumbnail URL": st.column_config.ImageColumn()},
                                 selection_mode="multi-row", hide_index=True, height=600)

        selected_indices = selection.get('selection', {}).get('rows', [])
        st.session_state.selected_image_ids = df.iloc[selected_indices]["ID"].tolist() if selected_indices else []

    @st.dialog('create', width='large')
    def render_create_dialog(self):
        st.subheader("Upload New Image")
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png", "gif"])

        if uploaded_file:
            col1, col2 = st.columns(2)
            col1.image(uploaded_file, use_container_width=True)
            col2.info(
                f"File name: {uploaded_file.name}\nFile type: {uploaded_file.type}\nFile size: {uploaded_file.size / 1024:.2f} KB")

            # Add scale factors selection
            st.subheader("Scale Factors")
            st.caption("Select resolution scales for the image:")
            col1, col2 = st.columns(2)
            scale_factors = []
            if col1.checkbox("1x (Original size)", value=True):
                scale_factors.append(1)
            if col1.checkbox("2x (Half size)"):
                scale_factors.append(2)
            if col2.checkbox("4x (Quarter size)"):
                scale_factors.append(4)
            if col2.checkbox("8x (⅛ size)"):
                scale_factors.append(8)
            if col2.checkbox("16x (⅟₁₆ size)"):
                scale_factors.append(16)

            if len(scale_factors) == 0:
                scale_factors = [1]
            col2.info(f"Selected scale factors: {', '.join([f'{s}x' for s in scale_factors])}")

            col_cancel, col_confirm = st.columns(2)
            if col_cancel.button("Cancel", key="cancel_create", use_container_width=True):
                st.rerun()
            if col_confirm.button("Confirm Upload", key="confirm_create", use_container_width=True):
                with st.spinner("Uploading image..."):
                    new_image = self.image_service.create(uploaded_file, scale_factors=scale_factors)
                    st.session_state.notification = {
                        'type': 'success' if new_image else 'error',
                        'message': f"Image uploaded successfully! ID: {new_image.id}" if new_image else "Failed to upload image."
                    }
                    st.rerun()

    @st.dialog('update', width='large')
    def render_update_dialog(self):
        image_id = st.session_state.selected_image_ids[0]
        st.subheader(f"Update Image ID: {image_id}")
        image = self.image_service.get_by_id(image_id)

        if image:
            col1, col2 = st.columns(2)
            col1.image(image.thumbnail_url, use_container_width=True)

            with col2:
                st.text("Image Properties")
                tag = st.text_input("Tag", value=image.tag or "", key="update_tag_input")
                used = st.checkbox("Mark as Used", value=image.used or False, key="update_used_checkbox")

            has_changes = (tag != (image.tag or "")) or (used != (image.used or False))

            col_cancel, col_confirm = st.columns(2)
            if col_cancel.button("Cancel", key="cancel_update", use_container_width=True):
                st.rerun()

            if col_confirm.button("Update", key="confirm_update",
                                  disabled=not has_changes,
                                  use_container_width=True):
                with st.spinner("Updating image..."):
                    update_data = {
                        "tag": tag,
                        "used": used
                    }

                    updated = self.image_service.update(image_id, update_data)

                    st.session_state.notification = {
                        'type': 'success' if updated else 'error',
                        'message': "Image updated successfully!" if updated else "Failed to update image."
                    }
                    st.rerun()

    @st.dialog('delete', width='large')
    def render_delete_dialog(self):
        selected_ids = st.session_state.selected_image_ids
        num_selected = len(selected_ids)
        st.subheader(f"Delete {num_selected} Image{'s' if num_selected > 1 else ''}")
        st.warning(f"You are about to delete {num_selected} images. This action cannot be undone.")
        if num_selected == 1:
            image = self.image_service.get_by_id(selected_ids[0])
            if image:
                col1, col2 = st.columns(2)
                col1.image(image.thumbnail_url, use_container_width=True)

        col_cancel, col_confirm = st.columns(2)
        if col_cancel.button("Cancel", key="cancel_delete", use_container_width=True):
            st.rerun()
        if col_confirm.button("Confirm Delete", key="confirm_delete", use_container_width=True):
            with st.spinner(f"Deleting {num_selected} image(s)..."):
                success_count = sum(self.image_service.delete(img_id) for img_id in selected_ids)
                st.session_state.notification = {
                    'type': 'success' if success_count == num_selected else 'warning',
                    'message': f"Successfully deleted {success_count} image(s)!" if success_count == num_selected else f"Deleted {success_count} out of {num_selected} images."
                }
                st.session_state.selected_image_ids = []
                st.rerun()

    @st.dialog('create_manifest', width='large')
    def render_create_manifest_dialog(self):
        selected_ids = st.session_state.selected_image_ids
        num_selected = len(selected_ids)
        st.subheader(f"Create Manifest with {num_selected} Image{'s' if num_selected > 1 else ''}")
        cols = st.columns(min(3, num_selected))
        img_info_list = []
        thumbnail_url = None
        for i, img_id in enumerate(selected_ids[:6]):
            image = self.image_service.get_by_id(img_id)
            if image:
                cols[i % len(cols)].image(image.thumbnail_url, width=150)
                img_info_list.append(image.info_url)
            if i == 0:
                thumbnail_url = image.thumbnail_url
        if num_selected > 6:
            st.info(f"... and {num_selected - 6} more images")

        manifest_tag = st.text_input("Manifest Tag", key="manifest_tag")

        col_cancel, col_confirm = st.columns(2)
        if col_cancel.button("Cancel", key="cancel_manifest", use_container_width=True):
            st.rerun()
        if col_confirm.button("Create Manifest", key="confirm_manifest", disabled=not manifest_tag.strip(), use_container_width=True):
            with st.spinner("Creating manifest..."):
                try:
                    iiif_image_list = []

                    for img_info in img_info_list:
                        resp = requests.get(img_info)
                        image_info_dt = resp.json()
                        iiif_image_list.append(IIIF3Image(**image_info_dt))

                    manifest_obj = self.image_service.create_manifest_by_image_info_list(
                        iiif_image_list=iiif_image_list,
                        tag=manifest_tag,
                        thumbnail_url=thumbnail_url
                    )
                    if manifest_obj:

                        for img_id in selected_ids[:6]:
                            self.image_service.update(img_id, {"used": True})

                        st.session_state.notification = {
                            'type': 'success',
                            'message': f"Manifest created successfully! ID: {manifest_obj.id}"
                        }
                        st.rerun()
                    else:
                        st.session_state.notification = {
                            'type': 'error',
                            'message': "Failed to create manifest."
                        }
                        st.rerun()
                except Exception as e:
                    st.session_state.notification = {
                        'type': 'error',
                        'message': f"Error creating manifest: {str(e)}"
                    }
                    st.rerun()

    def render(self):

        self.render_notification()
        self.render_header_section()
        query = self.render_search_section()
        self.render_dataframe_section(query)
        create_button, update_button, delete_button, create_manifest_button = self.render_action_section()
        if create_button:
            self.render_create_dialog()
        if update_button:
            self.render_update_dialog()
        if delete_button:
            self.render_delete_dialog()
        if create_manifest_button:
            self.render_create_manifest_dialog()


@inject
def image_view(image_service: Annotated[ImageService, Provide[AppContainer.image_service]]) -> None:
    try:
        st.set_page_config(
            page_title="Image Management",
            page_icon="🖼️",
            layout="wide"
        )
    except StreamlitSetPageConfigMustBeFirstCommandError:
        pass

    check_authentication()
    ImageView(image_service).render()