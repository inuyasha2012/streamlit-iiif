from typing import Iterator, Union, Any, List

from langchain_core.messages import HumanMessage, AnyMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from utils.agent import parser_manifest, get_analyze_image_with_query


class AgentService:

    def __init__(self, text_llm_client: ChatOpenAI, vl_llm_client: ChatOpenAI):
        self.llm = text_llm_client
        self.vk_llm = vl_llm_client
        prompt = """You are an advanced IIIF (International Image Interoperability Framework) assistant.\n 
            Your capabilities include working with digital image collections, manuscripts, and cultural heritage materials.\n  
            You can assist users in three main ways:\n
            1. "parse" - When they want to view, analyze, or query information from an existing IIIF resource\n
            2. "annotate" - When they want to add annotations or tags to IIIF content\n
            3. "build" - When they want to create or modify IIIF resources or their properties\n
            Respond only to IIIF-related queries, providing helpful information about:\n
            - Manifest structure, metadata, and contained images\n
            - Image annotation and viewing capabilities\n
            - Best practices for IIIF resource creation and modification\n
            """
        self.graph = create_react_agent(
            model=self.llm,
            tools=[parser_manifest, get_analyze_image_with_query(vl_llm_client)],
            prompt=prompt,
        )

    def invoke(self, messages: List[AnyMessage]) -> Union[dict[str, Any], Any]:
        inputs = {"messages": messages}
        response = self.graph.invoke(inputs, stream_mode="values")
        return response

    def stream(self, question: str) -> Iterator[Union[dict[str, Any], Any]]:
        inputs = {"messages": [HumanMessage(question)]}
        stream = self.graph.stream(inputs, stream_mode="values")
        return stream