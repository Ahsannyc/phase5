import cohere
from typing import Optional
import os


class CohereClientWrapper:
    """Wrapper for Cohere API client."""

    def __init__(self):
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ValueError("COHERE_API_KEY environment variable not set")
        self.client = cohere.ClientV2(api_key=api_key)

    def chat(
        self,
        messages: list[dict],
        model: str = "command-r-plus",
        tools: list[dict] = None,
    ) -> dict:
        """Send a message to Cohere and get a response."""
        response = self.client.chat(
            model=model,
            messages=messages,
            tools=tools,
        )

        # Extract text content from response
        content = ""
        if hasattr(response.message, 'content'):
            # Handle list of content blocks
            if isinstance(response.message.content, list):
                for block in response.message.content:
                    if hasattr(block, 'text'):
                        content += block.text
            else:
                content = str(response.message.content)

        return {
            "content": content or "I'm ready to help with your tasks!",
            "stop_reason": getattr(response, 'stop_reason', 'end_turn'),
            "tool_calls": getattr(response.message, 'tool_calls', None),
        }

    def get_available_models(self) -> list[str]:
        """Get list of available Cohere models."""
        return ["command-r-plus", "command-r", "command"]
