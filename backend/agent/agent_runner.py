"""Agent runner for orchestrating AI conversations and tool calls."""

from typing import Optional, Any
from backend.app.services.cohere_client import CohereClientWrapper


class AgentRunner:
    """Orchestrates conversation flow using LLM and tools."""

    def __init__(self):
        self.cohere_client = CohereClientWrapper()
        self.available_tools = []

    def register_tool(self, tool: dict):
        """Register a tool that the agent can use."""
        self.available_tools.append(tool)

    async def process_message(
        self,
        user_message: str,
        conversation_history: list[dict],
        user_id: int,
    ) -> dict:
        """Process a user message and return agent response."""
        # Add user message to history
        messages = conversation_history + [
            {"role": "user", "content": user_message}
        ]

        # Get response from LLM
        response = self.cohere_client.chat(
            messages=messages,
            tools=self.available_tools,
        )

        return {
            "content": response["content"],
            "tool_calls": response["tool_calls"],
            "stop_reason": response["stop_reason"],
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return """You are a helpful AI assistant for managing Todo tasks.
You help users organize their tasks through natural language conversation.
Always confirm actions before executing them.
Ask for clarification when requests are ambiguous.
Be friendly and supportive."""
