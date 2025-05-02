from typing import Tuple, Annotated, cast, TypedDict
import streamlit as st
from sqlalchemy.orm import InstrumentedAttribute
from streamlit_extras.row import row
from dependency_injector.wiring import inject, Provide
from container import AppContainer
from services import ManifestService
from services.ai import AnnotationService


class ManifestTypedDict(TypedDict):
    id: InstrumentedAttribute[int]
    manifest_url: InstrumentedAttribute[str]
    annotated: InstrumentedAttribute[bool]


class AnnoView:
    def __init__(self,
                 manifest_service: ManifestService,
                 annotation_service: AnnotationService):
        self.manifest_service = manifest_service
        self.annotation_service = annotation_service

    @staticmethod
    def page_header_render():
        st.title("Annotation")
        st.write("Annotation for IIIF 3.0 Manifests")

    def page_dataframe_render(self) -> ManifestTypedDict | None:
        st.write("Manifest List")
        objs = self.manifest_service.filter_by_public()
        manifest_list = [{'id': obj.id, 'manifest_url': obj.manifest_url, 'annotated': obj.annotated} for obj in objs]
        selection = st.dataframe(
            manifest_list,
            use_container_width=True,
            selection_mode='single-row',
            on_select="rerun",
        )
        selected_indices = selection.get('selection', {}).get('rows', [])
        if selected_indices:
            selected_index = selected_indices[0]
            return manifest_list[selected_index]
        return None

    @staticmethod
    def page_action_render(manifest: ManifestTypedDict | None) -> Tuple[str, bool]:
        left, right = st.columns(2, vertical_alignment='bottom')
        anno_type = left.selectbox(
            label='select annotation type',
            # TODO fix options or add comments method
            options=['Image Detections', 'Image Comments'],
        )
        anno_button = right.button('Annotate', use_container_width=True, disabled=manifest is None)
        return anno_type, anno_button

    # @st.dialog('annotation_dialog', width='large')
    def page_body_render(self, manifest: ManifestTypedDict) -> None:
        each_row = row([0.3, 0.7])
        manifest_url = cast(str, manifest['manifest_url'])
        manifest_id =cast(int, manifest['id'])
        with st.spinner("Processing annotations..."):
            result = self.annotation_service.process_manifest_annotations(manifest_url)

            # Display each image and its annotations
            for item in result["results"]:
                each_row.image(item["image_url"], use_container_width=True)
                each_row.write(item["annotation_data"] or {})

            # Save updated manifest
            uuid = result["uuid"]
            # TODO add method to ManifestService to update manifest info file
            self.manifest_service.update_manifest_info_file(uuid, result["manifest_json"])
            self.manifest_service.update(manifest_id, {'annotated': True})

        st.divider()
        st.write("Manifest updated with annotations.")
        st.json(result["manifest_json"])

    def render(self) -> None:
        st.set_page_config(page_title="Manifest Image Viewer", page_icon="🖼️", layout="wide")
        self.page_header_render()
        st.divider()
        manifest = self.page_dataframe_render()
        anno_type, anno_btn = self.page_action_render(manifest)
        if manifest and anno_btn:
            self.page_body_render(manifest)


@inject
def anno_view(
        manifest_service: Annotated[ManifestService, Provide[AppContainer.manifest_service]],
        annotation_service: Annotated[AnnotationService, Provide[AppContainer.annotation_service]]
) -> None:
    AnnoView(manifest_service, annotation_service).render()