# GitOps Deployment Pattern Skill

Name: GitOps Deployment Pattern

Instructions:
Setup GitOps-style continuous deployment via ArgoCD or Flux

Responsibilities:
- Generate ArgoCD Application manifests for automated GitOps sync
- Configure Git repository as source of truth
- Implement auto-sync and pruning policies
- Set up ApplicationSet for multi-environment deployments
- Monitor sync status and health checks
- Document GitOps workflow and rollback procedures

Strict rules:
- Use ArgoCD or Flux (ArgoCD recommended for Todo project)
- No manual kubectl apply; all changes via Git
- Enable prune to clean up removed resources
- Implement sync notifications and alerting
- All manifests in Git repo (infrastructure-as-code)

Current project: Phase 5 – GitOps production flow with continuous deployment

## Implementation Steps

1. Install ArgoCD in Kubernetes cluster (helm install argocd)
2. Create Git repository for application manifests
3. Generate ArgoCD Application YAML with:
   - Git repository source
   - Target namespace and cluster
   - Sync policy (auto-sync, pruning, self-heal)
4. Implement ApplicationSet for dev/staging/prod environments
5. Configure webhook triggers for Git push events
6. Setup ArgoCD notifications (Slack, email, etc.)
7. Configure health assessment policies
8. Document rollback procedure (revert Git commit, ArgoCD auto-syncs)
9. Test sync status monitoring and remediation
10. Verify auto-healing on manual pod deletion

## Execution

This skill coordinates with the Blueprint GitOps Engineer and Cloud Deployment Engineer agents to establish GitOps-driven continuous deployment and infrastructure-as-code practices.
