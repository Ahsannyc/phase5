"""Agent runner for orchestrating AI conversations and tool calls."""

from typing import Optional, Any
import re
from app.services.cohere_client import CohereClientWrapper
from app.agent.prompts import get_system_prompt


class AgentRunner:
    """Orchestrates conversation flow using LLM and tools."""

    def __init__(self):
        self.cohere_client = CohereClientWrapper()

    async def process_message(
        self,
        user_message: str,
        conversation_history: list,
        user_id: int,
        tools: Any,
    ) -> dict:
        """Process a user message and execute appropriate tools."""

        intent, params = self._parse_intent(user_message)

        try:
            if intent == "add_task":
                result = await tools.add_task(user_id, params["title"], params.get("description"))
                ai_response = result["message"]

            elif intent == "list_tasks":
                result = await tools.list_tasks(user_id, params.get("completed_only", False))
                ai_response = result["message"]

            elif intent == "complete_task":
                if "task_id" not in params or not params["task_id"]:
                    ai_response = "❓ Which task would you like to mark as complete? Please provide the task number."
                else:
                    result = await tools.complete_task(user_id, params["task_id"])
                    ai_response = result["message"]

            elif intent == "delete_task":
                if "task_id" not in params or not params["task_id"]:
                    ai_response = "❓ Which task would you like to delete? Please provide the task number."
                else:
                    ai_response = f"⚠️ Are you sure you want to delete task {params['task_id']}? Reply 'yes' or 'confirm' to proceed."

            elif intent == "update_task":
                if "task_id" not in params or not params["task_id"]:
                    ai_response = "❓ Which task would you like to update? Please provide the task number."
                else:
                    result = await tools.update_task(user_id, params["task_id"], params.get("title"), params.get("description"))
                    ai_response = result["message"]

            else:
                ai_response = await self._get_llm_response(user_message, conversation_history)

            return {
                "content": ai_response,
                "tool_calls": None,
                "stop_reason": "end_turn",
            }

        except Exception as e:
            return {
                "content": f"❌ An error occurred: {str(e)}. Please try again.",
                "tool_calls": None,
                "stop_reason": "error",
            }

    def _parse_intent(self, user_message: str) -> tuple:
        """Parse user message to determine intent and extract parameters."""

        message_lower = user_message.lower().strip()

        if any(phrase in message_lower for phrase in ["add task", "create task", "new task"]):
            for keyword in ["add task", "create task", "new task"]:
                if keyword in message_lower:
                    title = user_message[user_message.lower().index(keyword) + len(keyword):].strip()
                    break
            return "add_task", {"title": title if title else "Untitled"}

        elif any(phrase in message_lower for phrase in ["list tasks", "show tasks", "get tasks", "my tasks", "all tasks", "list all"]):
            return "list_tasks", {}

        elif any(phrase in message_lower for phrase in ["mark done", "mark complete", "complete task", "finish task", "done"]):
            task_id = self._extract_task_id(message_lower)
            return "complete_task", {"task_id": task_id}

        elif any(phrase in message_lower for phrase in ["delete task", "remove task", "delete"]):
            task_id = self._extract_task_id(message_lower)
            return "delete_task", {"task_id": task_id}

        elif any(phrase in message_lower for phrase in ["update task", "edit task", "change task"]):
            task_id = self._extract_task_id(message_lower)
            for keyword in ["update task", "edit task", "change task"]:
                if keyword in message_lower:
                    rest = user_message[user_message.lower().index(keyword) + len(keyword):].strip()
                    rest = re.sub(r'^\d+\s+', '', rest).strip()
                    return "update_task", {"task_id": task_id, "title": rest if rest else None}

        return "unclear", {}

    def _extract_task_id(self, message: str) -> Optional[int]:
        """Extract task ID number from message."""
        numbers = re.findall(r'\b(\d+)\b', message)
        if numbers:
            return int(numbers[0])
        return None

    async def _get_llm_response(self, user_message: str, conversation_history: list) -> str:
        """Get response from LLM for general conversation."""

        messages = conversation_history + [{"role": "user", "content": user_message}]

        try:
            response = self.cohere_client.chat(
                messages=messages,
                model="command-r-plus",
            )
            return response["content"]
        except Exception as e:
            return "I'm having trouble understanding that request. Could you try rephrasing?"
