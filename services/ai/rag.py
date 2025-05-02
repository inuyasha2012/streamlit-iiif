from typing import Iterator

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from repositories.ai import RetrieverRepository
from langchain_openai import ChatOpenAI


class RAGService:

    def __init__(self, vl_llm_client: ChatOpenAI, retriever_repository: RetrieverRepository):
        self.llm = vl_llm_client
        self.retriever_repository = retriever_repository

    @staticmethod
    def extract_media_context(document_metadata):
        """Extract image URLs and their associated metadata from document references.

        Processes document metadata that may contain manifest references and
        returns a structured dictionary with image URLs and contextual metadata.
        """
        image_urls = []
        context_descriptions = []
        for doc in document_metadata:
            try:
                manifest_url, image_url = doc.decode().split('|')
                image_urls.append(image_url)
                context_description = f'{image_url} belongs to {manifest_url}'
                context_descriptions.append(context_description)
            except ValueError:
                image_urls.append(doc.decode())
        return {"image_urls": image_urls, "context_descriptions": context_descriptions}

    @staticmethod
    def img_prompt_func(data_dict):
        messages = []

        image_urls = []
        context_descriptions = []

        if data_dict["context"]["image_urls"]:
            for image_url in data_dict["context"]["image_urls"]:
                image_message = {
                    "type": "image_url",
                    "image_url": {"url": image_url},
                }
                messages.append(image_message)
                image_urls.append(image_url)
        if data_dict["context"]["context_descriptions"]:
            context_descriptions = data_dict["context"]["context_descriptions"]


        # Add chat history context
        chat_history_text = ""
        if "chat_history" in data_dict and data_dict["chat_history"]:
            for message in data_dict["chat_history"]:
                if isinstance(message, HumanMessage):
                    chat_history_text += f"Human: {message.content}\n"
                elif isinstance(message, AIMessage):
                    chat_history_text += f"AI: {message.content}\n"

        # Add the text for analysis with chat history
        text_message = {
            "type": "text",
            "text": (
                "You will be given image(s).\n"
                f"Chat history:\n{chat_history_text}\n"
                "Analyze the provided image(s) carefully. Based on the user's question and chat history:\n"
                "1. First determine if the image(s) are relevant to the user's query.\n"
                "2. If the image(s) ARE relevant:\n"
                "   a. Identify key visual elements in the images that answer the question\n"
                "   b. Provide a detailed analysis of these visual elements\n"
                "   c. Answer the user's question clearly and concisely based on the image content\n"
                "   d. If the image contains text, reference any important textual information\n"
                "   e. IMPORTANT: Include the image in your response for reference\n"
                "   f. IMPORTANT: Include the IIIF manifest URL these images belong to\n"
                "3. If the image(s) are NOT relevant to the query:\n"
                "   a. Politely inform the user that our repository doesn't contain images matching their query\n"
                "   b. Suggest alternative queries that might yield better results\n"
                "   c. Offer to help with a different question if possible\n"
                "4. Use Markdown formatting in your response:\n"
                "   a. Include images url as: ![description](image_url)\n"
                "   b. Include manifest url as: [IIIF Manifest Url](manifest_url)\n"
                f"For the question: {data_dict['question']}\n"
                f"Referenced image URLs: {', '.join(image_urls)}\n"
                f"Context descriptions: {', '.join(context_descriptions)}\n"
            ),
        }
        messages.append(text_message)
        return [HumanMessage(content=messages)]

    def get_chain(self, chat_history=None):
        if chat_history is None:
            chat_history = []

        chain = (
                {
                    "context": self.retriever_repository.retriever | RunnableLambda(self.extract_media_context),
                    "question": RunnablePassthrough(),
                    "chat_history": lambda _: chat_history,
                }
                | RunnableLambda(self.img_prompt_func)
                | self.llm
                | StrOutputParser()
        )

        return chain


    def invoke(self, question: str, chat_history=None) -> str:
        chain = self.get_chain(chat_history)
        response = chain.invoke(question)
        return response

    def stream(self, question: str, chat_history=None) -> Iterator[str]:
        chain = self.get_chain(chat_history)
        stream = chain.stream(question)
        return stream
