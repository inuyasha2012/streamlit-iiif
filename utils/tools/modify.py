from typing import NamedTuple, List, Dict, Any, NoReturn

from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class Config(NamedTuple):
    api_key: str
    model: str
    base_url: str


class ImageDescriptiveProperty(BaseModel):
    """
    Pydantic model representing descriptive properties for images in IIIF presentation API.
    Encapsulates key metadata elements required for IIIF manifest generation:
    - Labels: Used as display titles in the manifest
    - Summary: Provides a concise description of image content
    - Metadata: Structured key-value pairs for additional image information

    This model serves as an intermediary structure between AI-generated image analysis
    and the formal IIIF manifest structure, facilitating the transformation of
    visual content to standardized presentation format.
    """
    label: List[str] = Field(..., description="List of display labels or titles for the image")
    summary: str = Field(..., description="summary of the image content")
    metadata: Dict[str, str] = Field(..., description="Metadata label for the image")


class ImageModifyAgent:


    def __init__(self, config: Config):
        self.llm = init_chat_model(
            model_provider='openai',
            api_key=config.api_key,
            model=config.model,
            base_url=config.base_url,
            streaming=True,
            temperature=0
        )

    def generate_descriptive_property_from_images(self, image_urls: List[str], language: str = "English") -> None | ImageDescriptiveProperty:

        prompt = ChatPromptTemplate(
            [
                (
                    "system",
                    """Use {language} Analyze these images and generate descriptive properties suitable for a IIIF presentation manifest.\n
                        1. LABELS: Create 2-4 concise, accurate titles that would serve as display labels for these images.\n
                           - Include the main subject or theme\n
                           - Consider historical or artistic significance\n
                           - Be specific but concise\n
                        2. SUMMARY: Write a single paragraph (3-5 sentences) that describes:\n
                           - What these images depicts\n
                           - Its notable visual elements\n
                           - Any historical, cultural, or artistic context apparent from these images\n
                           - The overall composition and style\n
                        3. METADATA: Generate 5-8 key-value pairs that provide structured information about these images:\n
                           - Subject matter (e.g., "Subject": "Landscape with mountains")\n
                           - Time period if evident (e.g., "Time Period": "19th century")\n
                           - Medium/technique if apparent (e.g., "Medium": "Oil painting")\n
                           - Style or artistic movement if relevant (e.g., "Style": "Impressionist")\n
                           - Composition details (e.g., "Composition": "Rule of thirds with central figure")\n
                           - Cultural context (e.g., "Cultural Context": "Japanese Edo period")\n
                           - Any other pertinent descriptive information\n
                        Focus on observable elements in these images rather than speculation. Ensure all descriptions are objective,\n
                        scholarly, and suitable for a cultural heritage or museum context.\n
                        {format_instructions}
                    """
                ),
                HumanMessage(content=[
                    {"type": "image_url", "image_url": {"url": image_url}} for image_url in image_urls
                ])
            ]
        )

        parser = PydanticOutputParser(pydantic_object=ImageDescriptiveProperty)
        format_instructions = parser.get_format_instructions()
        for _ in range(5):
            try:
                response = (prompt | self.llm).invoke({'language': language, 'format_instructions': format_instructions})
                return parser.parse(response.content)
            except Exception as e:
                print(f"Error: {e}")
                continue
        return None
