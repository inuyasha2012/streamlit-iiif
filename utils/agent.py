from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import tool, BaseTool
import requests
from typing import NoReturn, Callable, Union
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

class ParserManifestSchema(BaseModel):
    manifest_url: str = Field(description="URL pointing to a IIIF manifest, The URL typically: Ends with manifest.json, "
                                          "May be a complete URL (starting with http:// or https://)")


@tool("parser_tool",
      description="Fetches and returns the IIIF manifest json text from the provided URL.",
      args_schema=ParserManifestSchema)
def parser_manifest(manifest_url: str) -> str | NoReturn:
        response = requests.get(manifest_url)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.text


def get_analyze_image_with_query(llm: ChatOpenAI) -> Union[BaseTool, Callable[[Union[Callable, Runnable]], BaseTool]]:

    class AnalyzeImageWithQuerySchema(BaseModel):
        image_url: str = Field(description="URL of the image to analyze")
        query: str = Field(description="Specific question or instruction for analyzing the image")

    @tool("analyze_image_with_query",
          description='Analyze an image with a specific query/question and return the analysis results',
          args_schema=AnalyzeImageWithQuerySchema)
    def analyze_image_with_query(image_url: str, query: str) -> str:
        prompt = """Analyze the provided image based on the specific query or instruction given.\n
                Guidelines for your analysis:\n
                1. Focus precisely on answering the user's query\n
                2. Provide detailed observations relevant to the question\n
                3. When appropriate, describe visual elements in context\n
                4. For historical or artistic images, include relevant cultural or historical context\n
                5. Be factual and objective in your descriptions\n
                6. When measurements or spatial relationships are important, be specific\n
                7. If the query asks for identification, provide the most accurate labels possible\n
                8. Structure your response clearly with appropriate organization\n
                Remember to address only what is visible in the image and what was specifically asked.
                """

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=[
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": 'text', "text": query}
            ])
        ]

        response = llm.invoke(messages)
        return response.content
    return analyze_image_with_query


