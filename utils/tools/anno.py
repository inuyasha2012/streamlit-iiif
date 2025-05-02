from typing import NamedTuple, List, Dict, Any, Optional

import requests
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from utils.iiif import IIIF3Manifest, IIIF3AnnotationTag, IIIF3Annotation, IIIF3AnnotationPage



class ImageDetection(BaseModel):
    """Model for object detection results with bounding boxes."""
    objects: List[Dict[str, Any]] = Field(
        description="List of detected objects with their bounding boxes, where each object has 'name', 'bbox' [x1, y1, x2, y2]"
    )


class ImageTags(BaseModel):
    """Model for image tagging and description."""
    tags: List[str] = Field(description="List of tags extracted from the image")
    description: str = Field(description="Brief description of the image content")


class ImageAnnoTool:
    """
    Tool for generating and managing IIIF annotations based on image analysis.
    Uses vision-language models to detect objects and create structured annotations.
    """
    def __init__(self, vl_llm_client: ChatOpenAI):
        """
        Initialize the annotation tool with a vision-language model client.

        Args:
            vl_llm_client: Vision-language model client for image analysis
        """
        self.llm = vl_llm_client
        self.manifest: Optional[IIIF3Manifest] = None

    def set_manifest(self, manifest_url: str) -> None:
        """
        Fetch and set the IIIF manifest from a URL.

        Args:
            manifest_url: URL of the IIIF manifest

        Raises:
            requests.exceptions.HTTPError: If manifest retrieval fails
        """
        try:
            response = requests.get(manifest_url)
            response.raise_for_status()
            self.manifest = IIIF3Manifest(**response.json())
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to retrieve manifest: {e}")

    def get_manifest_images(self) -> List[str]:
        """
        Extract all image URLs from the loaded manifest.

        Returns:
            List of image URLs from the manifest
        """
        # TODO: Refactor this to use IIIF3Manifest
        if self.manifest is None:
            return []

        image_urls = []
        for canvas in self.manifest.items:
            for annotation_page in canvas.items:
                for annotation in annotation_page.items:
                    if hasattr(annotation.body, 'id'):
                        image_urls.append(annotation.body.id)
        return image_urls

    def set_anno4manifest(self, anno_data: Optional[ImageDetection], page_idx: int) -> None:
        """
        Add annotations to the manifest based on detection data.

        Args:
            anno_data: Detection data containing objects and bounding boxes
            page_idx: Index of the canvas/page to annotate

        Raises:
            ValueError: If manifest is not set or page_idx is invalid
        """
        if self.manifest is None:
            raise ValueError("Manifest not set. Call set_manifest() first.")

        if anno_data is None:
            return

        manifest = self.manifest

        if not (0 <= page_idx < len(manifest.items)):
            raise ValueError(f"Invalid page index: {page_idx}")

        canvas_id = manifest.items[page_idx].id
        page_id = manifest.items[page_idx].items[0].id
        annotated_id = manifest.items[page_idx].items[0].items[0].id

        iiif3_anno_list = []
        for obj_idx, obj in enumerate(anno_data.objects):
            tag = IIIF3AnnotationTag(value=obj['name'])
            bbox = obj['bbox']
            width = max(1, bbox[2] - bbox[0])
            height = max(1, bbox[3] - bbox[1])

            iiif3_anno = IIIF3Annotation(
                id=f'{annotated_id}/{obj_idx + 1}',
                motivation='tagging',
                body=tag,
                target=f'{canvas_id}#xywh={bbox[0]},{bbox[1]},{width},{height}'
            )
            iiif3_anno_list.append(iiif3_anno)

        manifest.items[page_idx].annotations = [
            IIIF3AnnotationPage(
                id=f'{page_id}/annotations/1',
                items=iiif3_anno_list
            )
        ]

    def generate_anno_data_from_image(self, image_url: str) -> Optional[ImageDetection]:
        """
        Generate object detection annotations from an image URL using vision-language model.

        Args:
            image_url: URL of the image to analyze

        Returns:
            ImageDetection object with detected objects and bounding boxes, or None if analysis fails
        """
        prompt = (
            """
            Analyze this image and detect all distinct objects. For each object:\n
            1. Provide a specific, accurate name (e.g., 'person', 'car', 'painting', 'building')\n
            2. Define a precise rectangular bounding box with pixel coordinates [x1, y1, x2, y2] where:\n
               - (x1, y1) is the top-left corner\n
               - (x2, y2) is the bottom-right corner\n
            3. If multiple similar objects exist, detect each one separately\n
            4. Prioritize detecting main subjects and clearly visible objects\n
            5. For artwork or historical images, identify key elements that would be valuable for cataloging\n
            Ensure coordinates remain within image boundaries and bounding boxes tightly surround each object.\n
            """
        )

        parser = PydanticOutputParser(pydantic_object=ImageDetection)
        format_instructions = parser.get_format_instructions()
        enhanced_prompt = f"{prompt}\n\n{format_instructions}"

        messages = [
            SystemMessage(content=enhanced_prompt),
            HumanMessage(content=[{"type": "image_url", "image_url": {"url": image_url}}])
        ]

        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                response = self.llm.invoke(messages)
                return parser.parse(response.content)
            except Exception as e:
                print(f"Attempt {attempt+1}/{max_attempts} failed: {e}")
                if attempt == max_attempts - 1:
                    print("All attempts to analyze image failed")
                    return None

        return None