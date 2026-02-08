# Implementation Tasks: Todo AI Chatbot

## Feature Overview
Implementation of a conversational AI chatbot that allows users to manage their personal Todo list using natural language after login. The chatbot supports 5 core Todo features through conversation, appears as a floating/chat icon in the UI, and uses Cohere LLM with OpenAI Agents SDK for tool orchestration.

## Phase 1: Setup
**Goal**: Establish project structure and foundational dependencies

- [X] T001 Create backend directory structure per implementation plan
- [X] T002 Create frontend directory structure per implementation plan
- [X] T003 [P] Add Cohere API dependency to backend requirements.txt
- [X] T004 [P] Add OpenAI Agents SDK dependency to backend requirements.txt
- [X] T005 [P] Add MCP SDK dependency to backend requirements.txt
- [X] T006 Update backend requirements.txt with all needed dependencies
- [X] T007 [P] Install ChatKit dependencies in frontend package.json
- [X] T008 [P] Install necessary TypeScript types in frontend package.json
- [X] T009 Set up backend project configuration
- [X] T010 Set up frontend project configuration

## Phase 2: Foundational
**Goal**: Implement core infrastructure needed for all user stories

- [X] T011 Create Conversation model in backend/app/models/conversation.py
- [X] T012 Create Message model in backend/app/models/message.py
- [X] T013 Update database migration files to include new models
- [X] T014 Create ConversationService in backend/app/services/conversation_service.py
- [X] T015 Create MessageService in backend/app/services/message_service.py
- [X] T016 Update existing TaskService for enhanced user validation
- [X] T017 Create Cohere client wrapper in backend/app/services/cohere_client.py
- [X] T018 Set up MCP server foundation in backend/mcp/server.py
- [X] T019 Set up agent foundation in backend/agent/agent_runner.py

## Phase 3: [US1] Add/Create Task via Chat
**Goal**: Enable users to add tasks via natural language in the chat interface

- [X] T020 [US1] Create add_task MCP tool in backend/mcp/tools.py
- [X] T021 [US1] Create frontend ChatInterface component in frontend/src/components/chat/ChatInterface.tsx
- [X] T022 [US1] Create chat API endpoint in backend/app/api/chat.py
- [X] T023 [US1] Implement basic agent prompt logic in backend/agent/prompts.py
- [X] T024 [US1] Connect chat endpoint to agent runner
- [X] T025 [US1] Add floating chat button to frontend UI
- [X] T026 [US1] Integrate chat API calls in frontend
- [X] T027 [US1] Test task creation via chat functionality

**Independent Test Criteria**: User can type "Add task buy groceries" in chat and see the task added to their list with confirmation message.

## Phase 4: [US2] View/List Tasks via Chat
**Goal**: Enable users to view their tasks via natural language in the chat interface

- [X] T028 [US2] Create list_tasks MCP tool in backend/mcp/tools.py
- [X] T029 [US2] Update agent prompt to recognize list commands
- [X] T030 [US2] Test listing tasks via chat functionality
- [X] T031 [US2] Enhance chat display to show task lists properly

**Independent Test Criteria**: User can type "Show my tasks" in chat and see their current task list displayed in the chat.

## Phase 5: [US3] Update/Edit Task via Chat
**Goal**: Enable users to update/edit tasks via natural language in the chat interface

- [X] T032 [US3] Create update_task MCP tool in backend/mcp/tools.py
- [X] T033 [US3] Update agent prompt to recognize update/edit commands
- [X] T034 [US3] Test task update via chat functionality

**Independent Test Criteria**: User can type "Change task 1 to buy groceries and milk" in chat and see the task updated with confirmation.

## Phase 6: [US4] Delete Task via Chat
**Goal**: Enable users to delete tasks via natural language in the chat interface

- [X] T035 [US4] Create delete_task MCP tool in backend/mcp/tools.py
- [X] T036 [US4] Update agent prompt to recognize delete commands
- [X] T037 [US4] Implement confirmation flow for deletions
- [X] T038 [US4] Test task deletion via chat functionality

**Independent Test Criteria**: User can type "Delete task 3" in chat and see confirmation request, then final deletion with confirmation.

## Phase 7: [US5] Mark Complete/Toggle via Chat
**Goal**: Enable users to mark tasks as complete via natural language in the chat interface

- [X] T039 [US5] Create complete_task MCP tool in backend/mcp/tools.py
- [X] T040 [US5] Update agent prompt to recognize completion commands
- [X] T041 [US5] Test task completion via chat functionality

**Independent Test Criteria**: User can type "Mark task 2 done" in chat and see the task marked as complete with confirmation.

## Phase 8: [US6] Enhanced Chat Experience
**Goal**: Improve user experience with conversation persistence and error handling

- [ ] T042 [US6] Implement conversation history persistence in chat
- [ ] T043 [US6] Add proper error handling to all MCP tools
- [ ] T044 [US6] Enhance agent to handle ambiguous requests with clarifications
- [ ] T045 [US6] Add typing indicators and loading states to chat UI
- [ ] T046 [US6] Implement graceful error messages in chat
- [ ] T047 [US6] Add conversation listing API endpoint
- [ ] T048 [US6] Add message history API endpoint

**Independent Test Criteria**: Chat maintains conversation state between sessions, shows loading indicators, handles errors gracefully, and allows users to view conversation history.

## Phase 9: Polish & Cross-Cutting Concerns
**Goal**: Complete the implementation with security, UI enhancements, and documentation

- [ ] T049 Implement JWT validation in chat endpoint middleware
- [ ] T050 Add user isolation validation to all MCP tools
- [ ] T051 Enhance frontend UI with AI-themed design (cyan/purple glow, glassmorphism)
- [ ] T052 Add proper loading animations during response processing
- [ ] T053 Implement toast notifications for error states
- [ ] T054 Add comprehensive logging for debugging
- [ ] T055 Update documentation with new API endpoints
- [ ] T056 Perform security audit of all new endpoints
- [ ] T057 Run integration tests for all chatbot functionality
- [ ] T058 Deploy and verify all functionality works end-to-end

## Dependencies

### User Story Dependencies
- US1 (Add Task) -> Base infrastructure (Phase 2)
- US2 (List Tasks) -> Base infrastructure (Phase 2)
- US3 (Update Task) -> Base infrastructure (Phase 2), US1
- US4 (Delete Task) -> Base infrastructure (Phase 2), US1
- US5 (Complete Task) -> Base infrastructure (Phase 2), US1
- US6 (Enhanced UX) -> All previous user stories

### Parallel Execution Opportunities
- T003-T005: Dependencies can be installed in parallel
- T020, T028, T032, T035, T39: MCP tools can be developed in parallel after foundation
- T021, T022: Frontend and backend chat components can develop in parallel
- T042-T048: Enhancement tasks in US6 can partially execute in parallel

## Implementation Strategy

### MVP Scope
The minimum viable product includes:
- US1: Ability to add tasks via chat (T020-T027)
- Basic conversation interface with floating chat button
- Core security with user isolation
- Simple agent that recognizes basic commands

### Incremental Delivery
1. Complete Phase 1-2: Foundation setup
2. Complete US1: Task creation via chat
3. Add US2-US5: Other task operations
4. Add US6: Enhanced UX features
5. Polish and deploy

This phased approach allows for early validation of the core concept while progressively adding features.