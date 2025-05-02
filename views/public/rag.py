import streamlit as st
from typing import Annotated, List, Dict
from dependency_injector.wiring import inject, Provide
from container import AppContainer
from services.ai import RAGService
from langchain_core.messages import HumanMessage, AIMessage


class RagView:
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service

    @staticmethod
    def page_header_render():
        st.title("💬 AI Knowledge Assistant")
        st.caption("🚀 A multimodal RAG-powered assistant")

    def initialize_chat(self):
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {"role": "assistant", "content": "How can I help you? You can ask about documents or images in our repository."}
            ]

        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

    def display_chat_history(self):
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

    def process_user_input(self):
        if prompt := st.chat_input("Ask a question..."):
            # Add user message to UI
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            # Add to chat history for RAG
            st.session_state.chat_history.append(HumanMessage(content=prompt))

            # Get RAG response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    content = self.rag_service.invoke(prompt, st.session_state.chat_history)
                    st.markdown(content)

            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": content})
            st.session_state.chat_history.append(AIMessage(content=content))

    def render(self):
        st.set_page_config(page_title="Knowledge Assistant", page_icon="💬", layout="wide")
        self.page_header_render()
        st.divider()
        self.initialize_chat()
        self.display_chat_history()
        self.process_user_input()


@inject
def rag_view(
    rag_service: Annotated[RAGService, Provide[AppContainer.rag_service]]
) -> None:
    """Entry point for the RAG view."""
    RagView(rag_service).render()


public_rag_page = st.Page(rag_view, url_path='rag', title="RAG", icon="📚")