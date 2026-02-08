# Map NL to Tools Skill

Name: Map NL to Tools

Instructions:
Guide agent to map natural language to correct MCP tools

Responsibilities:
- "Add task / create / remember to / I need to ..." → add_task
- "Show / list / what are my tasks / pending / completed" → list_tasks
- "Done / complete / finished / mark as done" → complete_task
- "Delete / remove / cancel" → delete_task
- "Change / update / edit / rename" → update_task
- Ambiguous (e.g. "delete meeting") → list_tasks first, then delete_task
- Always respond in friendly natural language
- Extract user_id from JWT context

Strict rules:
- Never guess – if unclear, ask user for clarification
- Always confirm action after tool use
- Use natural, conversational tone

Current project: Phase III – natural language understanding for Todo actions

## Implementation Steps

1. Create natural language processing logic for intent recognition
2. Implement mapping from phrases to appropriate MCP tools
3. Add disambiguation logic for unclear requests
4. Build friendly confirmation responses
5. Extract and validate user_id from JWT
6. Implement fallback questioning for ambiguous inputs
7. Test various phrasing patterns for robust recognition

## Execution

This skill will coordinate with the AI Agent Engineer agent to implement the required functionality.