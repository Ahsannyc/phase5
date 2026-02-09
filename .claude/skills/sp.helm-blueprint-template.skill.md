# Helm Blueprint Template Skill

Name: Helm Blueprint Template

Instructions:
Create reusable Helm blueprint for Todo app microservices

Responsibilities:
- Design parameterized Chart.yaml structure
- Create values.yaml with environment-specific configs (dev, staging, prod)
- Implement Kubernetes manifests (Deployment, Service, Ingress, Secret, ConfigMap)
- Use Helm templating functions for conditional logic
- Support external-secrets operator for secrets management
- Document override patterns and best practices

Strict rules:
- No hard-coded values; all configurable via values.yaml
- Support multiple environments via values overrides
- Include resource requests/limits
- Use image digest pinning for production
- Document all parameter meanings and defaults

Current project: Phase 5 – reusable cloud-native blueprints

## Implementation Steps

1. Create Helm chart directory structure (Chart.yaml, values.yaml, templates/)
2. Define Chart.yaml with metadata (name, version, appVersion, maintainers)
3. Create base values.yaml with defaults for all parameters
4. Implement Deployment template with:
   - Image, replicas, resource limits
   - Environment variables from ConfigMap/Secret
   - Health checks (livenessProbe, readinessProbe)
5. Create Service template with ClusterIP/LoadBalancer options
6. Create Ingress template with TLS support
7. Implement ConfigMap and Secret templates
8. Add external-secrets operator integration
9. Create values-dev.yaml, values-staging.yaml, values-prod.yaml
10. Add Helm packaging and deployment documentation

## Execution

This skill coordinates with the Blueprint GitOps Engineer agent to create reusable, parameterized infrastructure templates for multi-environment deployment.
