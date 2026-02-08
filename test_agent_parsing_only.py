"""Test agent parsing without dependencies."""

import re
from typing import Optional, Tuple


class SimpleAgentTest:
    """Simplified agent for testing parsing."""

    def _parse_intent(self, user_message: str) -> Tuple[str, dict]:
        """Parse user message to determine intent and extract parameters."""
        message_lower = user_message.lower().strip()

        if any(phrase in message_lower for phrase in ["add task", "create task", "new task"]):
            for keyword in ["add task", "create task", "new task"]:
                if keyword in message_lower:
                    title = user_message[user_message.lower().index(keyword) + len(keyword):].strip()
                    break
            return "add_task", {"title": title if title else "Untitled"}

        elif any(phrase in message_lower for phrase in ["list tasks", "show tasks", "get tasks", "my tasks"]):
            return "list_tasks", {}

        elif any(phrase in message_lower for phrase in ["mark done", "mark complete", "complete task", "done"]):
            task_id = self._extract_task_id(message_lower)
            return "complete_task", {"task_id": task_id}

        elif any(phrase in message_lower for phrase in ["delete task", "remove task"]):
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


def main():
    print("\n🧪 AGENT PARSING TEST\n")
    print("=" * 70)

    agent = SimpleAgentTest()

    test_cases = [
        ("Add task buy groceries", "add_task", "Untitled or actual title"),
        ("Create a new task for laundry", "add_task", "for laundry"),
        ("Show my tasks", "list_tasks", "{}"),
        ("List all tasks", "list_tasks", "{}"),
        ("Mark task 1 done", "complete_task", "task_id: 1"),
        ("Complete task 2", "complete_task", "task_id: 2"),
        ("Delete task 3", "delete_task", "task_id: 3"),
        ("Update task 1 to new name", "update_task", "task_id: 1"),
        ("Tell me about the weather", "unclear", "{}"),
    ]

    passed = 0
    failed = 0

    for message, expected_intent, note in test_cases:
        intent, params = agent._parse_intent(message)
        is_correct = intent == expected_intent
        status = "✅" if is_correct else "❌"

        if is_correct:
            passed += 1
        else:
            failed += 1

        print(f"{status} Input: '{message}'")
        print(f"   Expected: {expected_intent} | Got: {intent}")
        if params:
            print(f"   Params: {params}")
        print()

    print("=" * 70)
    print(f"\n📊 Results: {passed} passed, {failed} failed out of {passed + failed} tests")

    if failed == 0:
        print("\n✅ ALL PARSING TESTS PASSED!\n")
        print("Next steps:")
        print("1. Install dependencies: pip install -r backend/requirements.txt")
        print("2. Run migrations: cd backend && alembic upgrade head")
        print("3. Set COHERE_API_KEY in backend/.env")
        print("4. Start backend: cd backend && uvicorn app.main:app --reload")
        print("5. Start frontend: cd frontend && npm install && npm run dev")
        print("6. Visit http://localhost:3000 and test the chat!")
    else:
        print(f"\n❌ {failed} tests failed")


if __name__ == "__main__":
    main()
