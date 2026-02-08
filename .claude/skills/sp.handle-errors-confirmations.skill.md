# Handle Errors & Confirmations Skill

Name: Handle Errors & Confirmations

Instructions:
Implement graceful errors and action confirmations

Responsibilities:
- Backend: Return friendly error messages (e.g. "Task not found", "Not your task")
- Always add confirmation in assistant response (e.g. "Task added!", "Done! Marked complete.")
- Frontend: Show error toasts (red), success toasts (green), loading spinner
- Handle common cases:
  - Tool not found / invalid params → "Sorry, I didn't understand. Try again?"
  - Task not owned → "This task doesn't belong to you."
  - 401 unauthorized → redirect to login
- Keep tone polite and helpful

Strict rules:
- Never expose raw errors to user
- Confirm every action visibly
- Use AI-themed styling for toasts (cyan success, rose danger)

Current project: Phase III – polished chatbot UX with error handling & confirmations

## Implementation Steps

1. Create backend error handling middleware/utils
2. Implement friendly error message responses for common cases
3. Add confirmation messages to assistant responses
4. Create frontend toast notification system
5. Implement AI-themed styling for toasts (cyan success, rose danger)
6. Add loading spinner during API calls
7. Implement 401 redirect to login
8. Test error handling for all tool types

## Execution

This skill will coordinate with both frontend and backend agents to implement the required functionality.