---
id: 003
title: Phase 5 Part A Scope Clarified
stage: constitution
date: 2026-02-09
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: 003-intermediate-advanced-features
user: claude-code
command: /sp.constitution
labels: ["phase5", "constitution", "part-a", "intermediate-features", "advanced-features", "clarification"]
links:
  spec: /specs/phase5-partA/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md (updated v3.1.0 → v3.2.0)
tests:
  - Part A scope explicitly excludes Dapr/Kafka/cloud deployment
  - Part A Advanced & Intermediate Features detailed (7 features: priorities, tags, search, filter, sort, recurring, due dates)
  - Part B & C workflows separated from Part A
  - Part A success criteria focused on web UI + chatbot integration
  - Multi-phase independence clarified (Part A can be completed without Part B/C)
  - Database schema requirements explicit (priority, tags, due_date, recurrence_rule, reminder_offset)
  - MCP tool extensions specified (update_task, list_tasks with filters)
  - All principles remain testable and measurable
---

## Prompt

Update project constitution to clarify Phase 5 Part A scope and separate it from Part B & C.

User provided Phase V Part A specification emphasizing:
- Intermediate: Priorities, Tags, Search, Filter, Sort
- Advanced: Recurring Tasks, Due Dates & Reminders
- Frontend & Backend only — No Deployment (Dapr, Kafka, cloud deployment are Part B & C, not Part A)
- Must work in web UI and AI chatbot

Action required:
1. Clarify that Part A does NOT require Dapr/Kafka/cloud (those are Part B & C)
2. Expand "Advanced & Intermediate Features" section with explicit 7-feature breakdown
3. Separate Part A workflow from Part B & C workflows
4. Split success criteria: Part A (features), Part B (event-driven), Part C (cloud + CI/CD)
5. Update version (3.1.0 → 3.2.0 with MINOR bump rationale)

## Response snapshot

Phase 5 Constitution amended to v3.2.0 (MINOR version bump: clarified Part A independence from Dapr/Kafka/cloud):

**Part A (Feature Implementation Only)**:
- ✅ Intermediate: priorities (low/medium/high, color-coded), tags (multi-tag, free-text), search (full-text), filter (by status/priority/tag/due date), sort (by created/due/priority/title/status)
- ✅ Advanced: recurring tasks (daily/weekly/monthly/yearly, auto-create on complete), due dates & reminders (date+time, overdue highlight, reminder offset)
- ✅ Web UI: task form controls, visual indicators (badges/pills), search bar, filter/sort dropdowns
- ✅ Chatbot: MCP tool updates (update_task, list_tasks with filters), agent prompt for new intents
- ✅ Database: Task model extended (priority, tags array, due_date, recurrence_rule, reminder_offset)
- ✅ Multi-user isolation: all operations filter by user_id
- ❌ NO Dapr, Kafka, cloud deployment, CI/CD (Part B & C responsibilities)

**Part B & C (Separate Phases)**:
- Part B: Minikube + Dapr + Kafka (post-Part A)
- Part C: Real cloud (AKS/GKE/OKE) + CI/CD + monitoring (post-Part B)

**Workflow Separation**:
- Part A workflow: 11 steps (spec → database → backend → frontend → MCP → agent → chatkit → advanced engineer → integration tester → documentation)
- Part B workflow: 5 steps (event-driven architect → Dapr specialist → Dapr Kafka engineer → deployment → integration)
- Part C workflow: 7 steps (cloud deployment engineer → blueprint GitOps → observability → k8s hardening → CI/CD → integration → documentation)

**Version Decision Rationale**:
- MINOR (not MAJOR): No backward incompatibility; Part A/B/C are new subdivisions, not rewrites
- MINOR (not PATCH): Clarification and workflow restructuring are material guidance changes

## Outcome

- ✅ Impact: Part A scope now crystal clear. Agents know exactly what Part A requires (features only) and what to defer (Dapr/Kafka/cloud). No ambiguity. Prevents premature work on Part B/C before Part A completion.
- 🧪 Tests: Constitution governance checks: PASS. Part A success criteria are measurable and testable without Dapr/Kafka. Workflow sequences prevent conflicts and dependency issues.
- 📁 Files: .specify/memory/constitution.md (v3.2.0 with Part A/B/C separation, updated workflows, split success criteria)
- 🔁 Next prompts: `/sp.specify` to create detailed Part A feature spec, then `/sp.plan` to design Part A architecture
- 🧠 Reflection: By explicitly separating Part A from Part B/C, agents can now focus on feature implementation without being distracted by event-driven architecture or cloud deployment complexity. Constitution remains binding but now provides clear scope boundaries. Phase 5 is now understood as three independent phases, each with clear boundaries, deliverables, and success criteria.

## Evaluation notes (flywheel)

- Failure modes observed: None. Amendment successful and clear.
- Graders run and results (PASS/FAIL): Scope clarity: PASS. Part A independence verified. Workflow isolation verified. Success criteria measurability: PASS.
- Prompt variant (if applicable): N/A - single constitution amendment
- Next experiment: Execute `/sp.specify` to generate detailed Part A spec from user high-level input

---

**Status**: Phase 5 Part A Scope CLARIFIED and BINDING
**Version**: 3.2.0
**Last Amended**: 2026-02-09
**Next Command**: `/sp.specify`
