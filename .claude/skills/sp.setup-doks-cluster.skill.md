# Setup DOKS Cluster Skill

Name: Setup DOKS Cluster

Instructions:
Provision DigitalOcean Kubernetes Service (DOKS) cluster

Responsibilities:
- Generate doctl commands or Terraform for DOKS cluster provisioning
- Configure node pool (3+ nodes, latest Kubernetes version)
- Enable monitoring and logging addons
- Configure kubeconfig context locally
- Validate cluster health and connectivity

Strict rules:
- Use doctl CLI or Terraform – no manual DigitalOcean dashboard clicks
- Store kubeconfig securely in ~/.kube/config
- No hard-coded API tokens; use environment variables
- Always validate cluster is ready before returning

Current project: Phase 5 – real cloud deployment infrastructure

## Implementation Steps

1. Install and configure doctl CLI with DigitalOcean API token
2. Generate DOKS cluster with 3+ nodes (s-2vcpu-4gb or larger)
3. Set Kubernetes version to latest stable
4. Enable monitoring addon (DigitalOcean Monitoring)
5. Enable logging addon if available
6. Retrieve and merge kubeconfig into local context
7. Validate cluster health with kubectl cluster-info
8. Run kubectl get nodes to confirm node readiness
9. Document cluster name, region, and kubeconfig path

## Execution

This skill coordinates with the Cloud Deployment Engineer agent to provision and validate the DOKS cluster for Phase 5 production deployment.
