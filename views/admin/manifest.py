import json

import streamlit as st

import pandas as pd
from dependency_injector.wiring import Provide, inject
from typing import Annotated, Tuple

from datetime import datetime, timedelta

from streamlit.errors import StreamlitSetPageConfigMustBeFirstCommandError

from views.common.base import InterfaceCrudView
from services import ManifestService
from container import AppContainer


class ManifestView(InterfaceCrudView):

    def __init__(self, manifest_service: ManifestService):
        self.manifest_service = manifest_service
        st.session_state.setdefault('notification', {'type': None, 'message': None})

    def render_header_section(self) -> None:
        st.title("IIIF Manifests")
        st.write("Manage IIIF manifests - create, view, update, and delete manifests")

    def render_notification(self) -> None:
        notification = st.session_state.notification
        notification_type = notification.get('type', '')
        if notification_type:
            getattr(st, notification_type)(notification['message'])
            st.session_state.notification = {'type': None, 'message': None}

    def render_search_section(self) -> Tuple[str, str, str, str]:
        with st.expander("Search Options", expanded=True):
            left, right = st.columns([1, 1])
            updated_at_start_date = left.date_input("updated After", value=datetime.now() - timedelta(days=30),
                                         key="manifest_start_date")
            updated_at_end_date = right.date_input("updated Before", value=datetime.now() + timedelta(days=1),
                                        key="manifest_end_date")
            tag_filter = st.text_input("tag", key="manifest_tag__filter")
            public_filter = st.multiselect("public", ["Yes", "No"], ["Yes", "No"],
                                           key="manifest_public__filter")
        return updated_at_start_date, updated_at_end_date, tag_filter, public_filter

    def render_dataframe_section(self,
                                 updated_at_start_date: str | None=None,
                                 updated_at_end_date: str | None=None,
                                 tag_filter: str | None=None,
                                 public_filter: str | None=None
                                 ) -> None:
        with st.container():
            manifests = self.manifest_service.filter(
                updated_at_start_date=updated_at_start_date,
                updated_at_end_date=updated_at_end_date,
                tag=tag_filter,
                public=public_filter
            )

            df = pd.DataFrame([{
                "ID": manifest.id,
                "Tag": manifest.tag,
                "Public": manifest.public,
                "Thumbnail URL": manifest.thumbnail_url,
                "Created": manifest.created_at.strftime('%Y-%m-%d %H:%M') if manifest.created_at else "",
                "Updated": manifest.updated_at.strftime('%Y-%m-%d %H:%M') if manifest.updated_at else "",
                "URL": manifest.manifest_url,
                "Metadata": json.dumps(manifest.meta_data)
            } for manifest in manifests])

            selection = st.dataframe(
                df,
                use_container_width=True,
                column_config={"Thumbnail URL": st.column_config.ImageColumn()},
                on_select="rerun",
                selection_mode="multi-row",
                hide_index=True,
                height=600,
            )

            selected_indices = selection.get('selection', {}).get('rows', [])
            st.session_state.selected_manifest_ids = df.iloc[selected_indices][
                "ID"].tolist() if selected_indices else []

    def render_action_section(self) -> Tuple[bool, bool, bool]:
        with st.sidebar:
            st.info("Actions")
            create_button = st.button("Create New Manifest", key="create_manifest", use_container_width=True)
            has_selection = len(st.session_state.get('selected_manifest_ids', [])) > 0
            single_selection = len(st.session_state.get('selected_manifest_ids', [])) == 1
            update_button = st.button("Update Manifest", key="update_manifest", disabled=not single_selection,
                                        use_container_width=True)
            delete_button = st.button("Delete Selected", key="delete_manifest", disabled=not has_selection,
                                        use_container_width=True)
            return create_button, update_button, delete_button

    @st.dialog('create', width='large')
    def render_create_dialog(self) -> None:
        st.subheader("Create New Manifest")

        with st.form("create_manifest_form"):
            tag = st.text_input("Tag", key="new_manifest_tag")
            public = st.checkbox("Public", key="new_manifest_public", value=False)
            manifest_url = st.text_input("Manifest URL", key="new_manifest_url")
            thumbnail_url = st.text_input("Thumbnail URL", key='new_manifest_thumbnail_url')
            df = pd.DataFrame([], columns=['key', 'value'])
            st.text("Metadata")
            edited_df = st.data_editor(df, use_container_width=True, num_rows='dynamic')
            meta_data = edited_df.to_dict(orient='records')
            col1, col2 = st.columns(2)
            cancel = col1.form_submit_button("Cancel", use_container_width=True)
            submit = col2.form_submit_button("Create", use_container_width=True)
            if cancel:
                st.rerun()
            if submit:
                try:
                    manifest_obj = self.manifest_service.create(
                        tag=tag,
                        public=public,
                        manifest_url=manifest_url,
                        thumbnail_url=thumbnail_url,
                        meta_data=meta_data
                    )

                    if manifest_obj:
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

    @st.dialog('update', width='large')
    def render_update_dialog(self) -> None:
        selected_ids = st.session_state.selected_manifest_ids
        if len(selected_ids) != 1:
            st.error("Please select exactly one manifest to update.")
            return

        manifest_id = selected_ids[0]
        manifest = self.manifest_service.get_by_id(manifest_id)
        if not manifest:
            st.error(f"Manifest with ID {manifest_id} not found.")
            return

        st.subheader(f"Update Manifest ID: {manifest_id}")

        with st.form("update_manifest_form"):
            tag = st.text_input("Tag", value=manifest.tag, key="update_manifest_tag")
            public = st.checkbox("Public", value=manifest.public, key="update_manifest_public")
            manifest_url = st.text_input("Manifest URL", value=manifest.manifest_url, key="update_manifest_url")
            thumbnail_url = st.text_input("Thumbnail URL", value=manifest.thumbnail_url,)
            df = pd.DataFrame(manifest.meta_data, columns=['key', 'value'])
            st.text("Metadata")
            edited_df = st.data_editor(df, use_container_width=True, num_rows='dynamic')
            meta_data = edited_df.to_dict(orient='records')
            col1, col2 = st.columns(2)
            cancel = col1.form_submit_button("Cancel", use_container_width=True)
            submit = col2.form_submit_button("Update", use_container_width=True)
            if cancel:
                st.rerun()
            if submit:
                try:
                    updated = self.manifest_service.update(
                        manifest_id,
                        {
                            "tag": tag,
                            "public": public,
                            "manifest_url": manifest_url,
                            'thumbnail_url': thumbnail_url,
                            'meta_data': meta_data
                        }
                    )
                    if updated:
                        st.session_state.notification = {
                            'type': 'success',
                            'message': f"Manifest updated successfully! ID: {manifest_id}"
                        }
                        st.rerun()
                    else:
                        st.session_state.notification = {
                            'type': 'error',
                            'message': "Failed to update manifest."
                        }
                        st.rerun()
                except Exception as e:
                    st.session_state.notification = {
                        'type': 'error',
                        'message': f"Error updating manifest: {str(e)}"
                    }
                    st.rerun()

    @st.dialog('delete', width='large')
    def render_delete_dialog(self) -> None:
        selected_ids = st.session_state.selected_manifest_ids
        num_selected = len(selected_ids)
        st.subheader(f"Delete {num_selected} Manifest{'s' if num_selected > 1 else ''}")
        st.warning(f"You are about to delete {num_selected} manifests. This action cannot be undone.")

        col_cancel, col_confirm = st.columns(2)
        if col_cancel.button("Cancel", key="cancel_delete", use_container_width=True):
            st.rerun()
        if col_confirm.button("Confirm Delete", key="confirm_delete", use_container_width=True):
            with st.spinner(f"Deleting {num_selected} manifest(s)..."):
                success_count = sum(self.manifest_service.delete(manifest_id) for manifest_id in selected_ids)
                st.session_state.notification = {
                    'type': 'success' if success_count == num_selected else 'warning',
                    'message': f"Successfully deleted {success_count} manifest(s)!" if success_count == num_selected else f"Deleted {success_count} out of {num_selected} manifests."
                }
                st.session_state.selected_manifest_ids = []
                st.rerun()

    def render(self) -> None:
        self.render_header_section()
        self.render_notification()
        updated_at_start_date, updated_at_end_date, tag_filter, public_filter = self.render_search_section()
        self.render_dataframe_section(updated_at_start_date, updated_at_end_date, tag_filter, public_filter)
        create_button, update_button, delete_button = self.render_action_section()

        if create_button:
            self.render_create_dialog()
        if update_button:
            self.render_update_dialog()
        if delete_button:
            self.render_delete_dialog()


@inject
def manifest_view(manifest_service: Annotated[ManifestService, Provide[AppContainer.manifest_service]]) -> None:
    try:
        st.set_page_config(
            page_title="IIIF Manifests",
            page_icon="📚",
            layout="wide"
        )
    except StreamlitSetPageConfigMustBeFirstCommandError:
        pass
    ManifestView(manifest_service).render()