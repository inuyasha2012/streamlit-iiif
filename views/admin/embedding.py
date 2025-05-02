from typing import Tuple, Annotated
import streamlit as st
from streamlit_extras.row import row as streamlit_extras_row
from dependency_injector.wiring import Provide, inject

from container import AppContainer
from services import ManifestService
from services.ai import EmbeddingService

class EmbeddingView:
    def __init__(self,
                manifest_service: ManifestService,
                embedding_service: EmbeddingService
                ):
        self.manifest_service = manifest_service
        self.embedding_service = embedding_service

    @staticmethod
    def page_header_render():
        st.title("Embedding")
        st.write("Convert text to embeddings and save to Chroma")

    def page_action_render(self) -> Tuple[str, bool]:
        objs = self.manifest_service.filter_by_public()
        manifest_urls = []
        for obj in objs:
            manifest_urls.append(obj.manifest_url)
        manifest_url = st.selectbox(
            label='Choose a manifest.json file from the list below to begin',
            options=manifest_urls,
        )
        anno_button = st.button('Annotate', use_container_width=True)
        return manifest_url, anno_button

    def page_body_render(self, manifest_url: str):
        each_row = streamlit_extras_row([0.3, 0.7])
        image_urls, canvas_list = self.embedding_service.extract_image_urls_and_canvases(manifest_url)
        summaries = []
        for image_index, image_url in enumerate(image_urls):
            each_row.image(image_url, use_container_width=True)
            image_summary_stream = self.embedding_service.generate_image_summary(image_url)
            image_summary = each_row.write_stream(image_summary_stream)
            summaries.append(image_summary)

        for canvas_index, canvas in enumerate(canvas_list):
            canvas_json = canvas.model_dump_json(exclude_none=True, by_alias=True)
            each_row.json(canvas_json)
            canvas_summary_stream = self.embedding_service.generate_canvas_summary(canvas_json)
            canvas_summary = each_row.write_stream(canvas_summary_stream)
            summaries[canvas_index] = summaries[canvas_index] = f"{summaries[canvas_index]}\n\n--- Canvas Information ---\n{canvas_summary}"

        # TODO : Add manifest json to the embedding
        with st.spinner("Processing images and generating embeddings..."):
            self.embedding_service.store_embeddings(manifest_url, image_urls, summaries)
            st.success('Saved to Chroma')

    def render(self):
        self.page_header_render()
        st.divider()
        manifest_url, anno_button = self.page_action_render()
        if anno_button:
            self.page_body_render(manifest_url)


@inject
def embedding_view(
        manifest_service: Annotated[ManifestService, Provide[AppContainer.manifest_service]],
        embedding_service: Annotated[EmbeddingService, Provide[AppContainer.embedding_service]]
) -> None:
    EmbeddingView(manifest_service, embedding_service).render()