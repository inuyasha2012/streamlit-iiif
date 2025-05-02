from typing import Iterator, List, Tuple, Dict, Any

import requests
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessageChunk
from langchain_openai import ChatOpenAI

from repositories.ai import RetrieverRepository
from utils.iiif import IIIF3Manifest, IIIF3Canvas


class EmbeddingService:
    def __init__(self, vl_llm_client: ChatOpenAI, text_llm_client: ChatOpenAI, retriever_repository: RetrieverRepository):
        self.vl_llm = vl_llm_client
        self.text_llm = text_llm_client
        self.retriever_repository = retriever_repository

    @staticmethod
    def get_manifest(manifest_url: str) -> IIIF3Manifest:
        response = requests.get(manifest_url)
        response.raise_for_status()
        manifest_data: Dict[str, Any] = response.json()
        return IIIF3Manifest(**manifest_data)


    def extract_image_urls_and_canvases(self, manifest_url: str) -> Tuple[List[str], List[IIIF3Canvas]]:
        # TODO: Refactor this to use Adapter
        manifest = self.get_manifest(manifest_url)
        image_urls = []
        canvas_list = []
        for canvas in manifest.items:
            canvas_list.append(canvas)
            for annotation_page in canvas.items:
                for annotation in annotation_page.items:
                    image_urls.append(annotation.body.id)
        return image_urls, canvas_list

    def generate_image_summary(self, image_url: str) -> Iterator[BaseMessageChunk]:
        prompt = """
            You are an assistant tasked with summarizing images for retrieval. \n
            These summaries will be embedded and used to retrieve the raw image. \n
            Describe this image in detail, focusing on:\n
            1. Main subjects and prominent objects\n
            2. Actions, activities or events depicted\n
            3. Visual characteristics (colors, style, composition)\n
            4. Any text, symbols, or identifiable elements\n
            5. Context, setting, or time period\n
            Please Give a concise summary of the image that is well optimized for retrieval.\n
            """
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=[{"type": "image_url", "image_url": {"url": image_url}}])
        ]
        return self.vl_llm.stream(messages)


    def generate_canvas_summary(self, canvas_json: str) -> Iterator[BaseMessageChunk]:
        prompt = """
            You are an assistant tasked with summarizing raw json for retrieval. \n
            These summaries will be embedded and used to retrieve the raw json. \n
            Give a concise summary of the raw json text that is well optimized for retrieval
            """
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=canvas_json)
        ]
        return self.text_llm.stream(messages)


    def store_embeddings(self, manifest_url: str, image_urls: List[str], summaries: List[str]) -> None:
        # TODO: Add manifest json to the embedding
        byte_summaries = [summary.encode('utf8') for summary in summaries]
        image_url_metadata = [
            f"{manifest_url}|{image_url}".encode('utf8') for image_url in image_urls
        ]
        self.retriever_repository.add_documents(byte_summaries, image_url_metadata)
