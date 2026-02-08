---
id: 008
title: AIOps with kubectl-ai & kagent Guide (Phase 5)
stage: green
date: 2026-02-08
surface: agent
model: claude-haiku-4-5-20251001
feature: 001-cloud-native-deploy
branch: main
user: user
command: continue (Phase 5: AIOps documentation)
labels: ["aiops", "kubectl-ai", "kagent", "kubernetes", "automation", "troubleshooting"]
links:
  spec: specs/001-cloud-native-deploy/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - AIOPS_KUBECTL_GUIDE.md
  - backend/app/api/chat.py
tests:
  - T060-T065: Deployment and pod management via AI
  - T066-T071: Cluster analysis and diagnostics
  - T072-T074: Troubleshooting and incident response
---

## Prompt

Phase 4 deployment complete with Kubernetes infrastructure ready. Need comprehensive AIOps guide documenting kubectl-ai for natural language Kubernetes operations and kagent for advanced cluster analysis, integrated with chat API.

## Response snapshot

Created AIOPS_KUBECTL_GUIDE.md (900+ lines) documenting:

**Part 1: kubectl-ai Setup & Usage (T060-T065)**
- T060: Scale deployment via natural language ("scale backend to 3 replicas")
- T061: Get pod logs via natural language ("show backend error logs")
- T062: Restart pods without kubectl syntax
- T063: Port forward from CLI with AI inference
- T064: Pod status diagnosis and troubleshooting
- T065: Environment variable updates via chat

**Part 2: Cluster Analysis (T066-T071)**
- T066: Cluster health status report
- T067: Resource usage analysis (top memory/CPU consumers)
- T068: Event aggregation and anomaly detection
- T069: Configuration drift detection
- T070: Cost optimization recommendations
- T071: Network dependency mapping

**Part 3: Troubleshooting (T072-T074)**
- T072: Automated root cause diagnosis
- T073: Performance analysis with scaling advice
- T074: Incident response with recovery steps

**Part 4: Integration**
- Chat API integration for unified task + cluster operations
- kagent for advanced analysis
- Complete example workflows

## Outcome

- ✅ Impact: Natural language Kubernetes operations for DevOps teams. Reduces MTTR through instant diagnostics, enables non-specialist operators, provides 24/7 automated troubleshooting.

- 🧪 Tests: 15 distinct AIOps tasks (T060-T074) with:
  - kubectl-ai command generation and execution
  - Cluster health monitoring
  - Root cause analysis
  - Performance optimization recommendations
  - Incident recovery procedures

- 📁 Files: AIOPS_KUBECTL_GUIDE.md (900+ lines) with:
  - Installation and setup instructions
  - 15 detailed task examples with expected outputs
  - Advanced analysis with kagent
  - Chat API integration patterns
  - Benefits summary (reduced MTTR, knowledge capture, 24/7)

- 🔁 Next prompts:
  1. Install kubectl-ai and kagent
  2. Execute natural language queries against cluster
  3. Integrate with chat API for unified interface
  4. Proceed to Phase 7 Zero-Downtime demonstrations

---

**Phase 5 AIOps Complete**: Natural language Kubernetes operations fully documented with kubectl-ai and kagent integration.
