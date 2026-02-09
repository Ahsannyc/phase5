# Kafka Topic & Producer Skill

Name: Kafka Topic & Producer

Instructions:
Setup Kafka topics and async producer in FastAPI

Responsibilities:
- Define Kafka topics (e.g., todo-events, user-events)
- Implement async producer using aiokafka or confluent-kafka-python
- Produce events on task create/update/delete actions
- Define event schema with user_id, task_id, action, timestamp
- Implement retry logic and error handling
- Ensure non-blocking event publishing

Strict rules:
- Use async producer (aiokafka recommended)
- Never block request handling on producer send
- Implement retry policies with backoff
- No blocking calls in FastAPI route handlers
- Log producer errors for debugging

Current project: Phase 5 – Kafka event bus and async messaging

## Implementation Steps

1. Install aiokafka or confluent-kafka-python library
2. Create Kafka producer configuration (brokers, auth, serialization)
3. Initialize async KafkaProducer in FastAPI startup event
4. Define event schema (Pydantic model with user_id, task_id, action, timestamp)
5. Create producer helper functions for publish_task_event()
6. Integrate event publishing into task creation/update/delete endpoints
7. Implement error handling with retry logic (exponential backoff)
8. Add logging for event publication success/failure
9. Test producer with Kafka broker (local or Confluent Cloud)
10. Document event topics and schema version management

## Execution

This skill coordinates with the Dapr Kafka Engineer agent to establish the Kafka event bus for async task operations and event-driven workflows.
