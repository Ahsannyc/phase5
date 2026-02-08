"""Quick test script to verify chat implementation."""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.agent.agent_runner import AgentRunner
from app.mcp.tools import TodoTools


async def test_agent_parsing():
    """Test intent parsing."""
    print("=" * 60)
    print("TESTING INTENT PARSING")
    print("=" * 60)

    agent = AgentRunner()

    test_cases = [
        ("Add task buy groceries", "add_task"),
        ("Create a new task for laundry", "add_task"),
        ("Show my tasks", "list_tasks"),
        ("List all tasks", "list_tasks"),
        ("Mark task 1 done", "complete_task"),
        ("Complete task 2", "complete_task"),
        ("Delete task 3", "delete_task"),
        ("Update task 1 to new name", "update_task"),
    ]

    for message, expected_intent in test_cases:
        intent, params = agent._parse_intent(message)
        status = "✅" if intent == expected_intent else "❌"
        print(f"{status} '{message}'")
        print(f"   Intent: {intent} (expected: {expected_intent})")
        if params:
            print(f"   Params: {params}")
        print()


async def test_agent_with_mock_tools():
    """Test agent with mock tools."""
    print("=" * 60)
    print("TESTING AGENT WITH MOCK TOOLS")
    print("=" * 60)

    class MockTools:
        async def add_task(self, user_id, title, description=None):
            return {
                "success": True,
                "message": f"✅ Task '{title}' created successfully!",
                "task": {"id": 1, "title": title, "completed": False}
            }

        async def list_tasks(self, user_id, completed_only=False):
            return {
                "success": True,
                "message": "📋 Here are your tasks:\n⭕ Task 1: Buy groceries\n⭕ Task 2: Study Python",
                "tasks": []
            }

        async def complete_task(self, user_id, task_id):
            return {
                "success": True,
                "message": f"✅ Task {task_id} marked as complete!",
                "task": {"id": task_id, "completed": True}
            }

    agent = AgentRunner()
    tools = MockTools()

    test_messages = [
        "Add task buy milk",
        "Show my tasks",
        "Mark task 1 done",
    ]

    for message in test_messages:
        print(f"\nUser: {message}")
        try:
            response = await agent.process_message(
                message,
                [],
                user_id=1,
                tools=tools
            )
            print(f"Agent: {response['content']}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def main():
    """Run all tests."""
    print("\n🧪 CHATBOT IMPLEMENTATION TEST SUITE\n")

    # Test parsing
    asyncio.run(test_agent_parsing())

    # Test with mock tools
    asyncio.run(test_agent_with_mock_tools())

    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run database migrations: cd backend && alembic upgrade head")
    print("2. Set COHERE_API_KEY in .env")
    print("3. Start backend: uvicorn app.main:app --reload")
    print("4. Start frontend: cd frontend && npm run dev")
    print("5. Open http://localhost:3000 and test the chat!")


if __name__ == "__main__":
    main()
