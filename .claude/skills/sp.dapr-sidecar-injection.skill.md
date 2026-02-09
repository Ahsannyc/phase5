# Dapr Sidecar Injection Skill

Name: Dapr Sidecar Injection

Instructions:
Add Dapr sidecar containers to Kubernetes deployments

Responsibilities:
- Annotate Deployments with Dapr-specific metadata
- Set dapr.io/enabled: "true"
- Configure dapr.io/app-id and dapr.io/app-port
- Generate Dapr component YAML files (pub/sub, state store)
- Use Redis or PostgreSQL as state store backend
- Ensure sidecar auto-injection is enabled in cluster

Strict rules:
- Follow official Dapr documentation and annotations
- Services must be stateless; state managed via Dapr
- No hardcoded service-to-service URLs; use Dapr service invocation

Current project: Phase 5 – event-driven architecture with Dapr

## Implementation Steps

1. Verify Dapr is installed in cluster (dapr --version)
2. Enable sidecar auto-injection namespace annotation
3. Add Dapr annotations to Deployment spec.template.metadata.annotations
4. Configure dapr.io/app-id (service name), dapr.io/app-port, dapr.io/protocol
5. Create Dapr component YAML for pub/sub (Kafka)
6. Create Dapr component YAML for state store (Redis or PostgreSQL)
7. Validate component deployment with dapr components list
8. Test pub/sub and state operations via Dapr APIs
9. Document component metadata and port configuration

## Execution

This skill coordinates with the Dapr Kafka Engineer agent to configure sidecars, components, and service-to-service communication patterns.
