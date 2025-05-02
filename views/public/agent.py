import streamlit as st
from typing import Annotated, List, Dict
from dependency_injector.wiring import inject, Provide
from langgraph.prebuilt.chat_agent_executor import AgentState

from container import AppContainer
from services.ai import AgentService
from langchain_core.messages import HumanMessage, AIMessage


class AgentView:
    def __init__(self, agent_service: AgentService):
        self.agent_service = agent_service

    @staticmethod
    def page_header_render():
        st.title("🤖 AI Agent Assistant")
        st.caption("🔍 An intelligent agent that can understand and perform tasks")

    def initialize_chat(self):
        if "agent_messages" not in st.session_state:
            st.session_state["agent_messages"] = [
                {"role": "assistant", "content": "Hello! I'm your AI agent assistant. How can I help you today?"}
            ]

        if "agent_chat_history" not in st.session_state:
            st.session_state["agent_chat_history"] = []

    def display_chat_history(self):
        for msg in st.session_state.agent_messages:
            st.chat_message(msg["role"]).write(msg["content"])

    def process_user_input(self):
        if prompt := st.chat_input("What would you like me to do?"):
            # Add user message to UI
            st.session_state.agent_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            # Add to chat history for Agent
            st.session_state.agent_chat_history.append(HumanMessage(content=prompt))
            prompt = st.session_state.agent_chat_history
            # Get Agent response
            with st.chat_message("assistant"):
                with st.spinner("Working on it..."):
                    response = self.agent_service.invoke(prompt)
                    content = response['messages'][-1].content
                    st.write(content)

            # Add assistant response to history
            st.session_state.agent_messages.append({"role": "assistant", "content": content})
            st.session_state.agent_chat_history.extend(response['messages'])

    def render(self):
        st.set_page_config(page_title="Agent Assistant", page_icon="🤖", layout="wide")
        self.page_header_render()
        st.divider()
        self.initialize_chat()
        self.display_chat_history()
        self.process_user_input()


@inject
def agent_view(
    agent_service: Annotated[AgentService, Provide[AppContainer.agent_service]]
) -> None:
    """Entry point for the Agent view."""
    AgentView(agent_service).render()


public_agent_page = st.Page(agent_view, url_path='agent', title="Agent", icon="🤖")