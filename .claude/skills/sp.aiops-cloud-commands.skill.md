# AIOps Cloud Commands Skill

Name: AIOps Cloud Commands

Instructions:
Generate and execute kubectl-ai and kagent prompts for intelligent cloud cluster operations

Responsibilities:
- Use kubectl-ai to generate kubectl commands from natural language prompts
- Use kagent for root-cause analysis of cluster failures
- Generate prompts for scaling, debugging, and resource optimization
- Analyze pod crashes and node issues
- Suggest HPA (Horizontal Pod Autoscaler) configurations
- Perform capacity planning and cost optimization
- Document AIOps workflows and best practices

Strict rules:
- Use real cluster context (never dry-run against wrong cluster)
- Always test commands with --dry-run before execution
- Document all prompts and their corresponding outputs
- Maintain audit trail of changes
- Use kagent for intelligent failure diagnosis

Current project: Phase 5 – advanced AIOps for production cluster management

## Implementation Steps

1. Install kubectl-ai and kagent plugins
2. Configure cluster context and API access
3. Create AIOps prompt library for common tasks:
   - Scale deployment to N replicas
   - Debug pod crash loop
   - Find nodes with high resource usage
   - Generate HPA recommendation
   - Analyze slow API responses
4. Test kubectl-ai with sample prompts
5. Implement kagent integration for failure detection
6. Create Prometheus/Grafana metrics queries via prompts
7. Setup alerting rules based on AIOps recommendations
8. Document prompt templates and expected outputs
9. Create runbooks for common AIOps scenarios
10. Test root-cause analysis with staged failure scenarios

## Execution

This skill coordinates with the Observability AIOps Agent and K8s Production Hardening agents to enable intelligent, AI-driven cluster management and proactive failure prevention.
