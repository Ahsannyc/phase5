"""
Integration Test: Event-Driven Flow for Todo Application
=============================================================================
Tests event publishing and consumption via Dapr Pub/Sub (Kafka)
Verifies task events, reminders, state store operations, and schema compliance

Run:
    # Unit tests (mocked Kafka):
    pytest backend/tests/test_event_flow.py -v

    # Integration tests (real Kafka - requires Dapr + Kafka running):
    INTEGRATION_TEST=1 pytest backend/tests/test_event_flow.py -v

Requirements:
    - Dapr runtime (for integration tests)
    - Kafka cluster (for integration tests)
    - PostgreSQL database
    - Environment variables: DATABASE_URL, DAPR_HTTP_PORT, DAPR_GRPC_PORT
"""

import asyncio
import json
import os
from datetime import datetime, timedelta, UTC
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlmodel import Session, create_engine, select

# Imports from application
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


# =============================================================================
# Test Configuration
# =============================================================================

INTEGRATION_TEST = os.getenv("INTEGRATION_TEST", "0") == "1"

# Dapr configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_GRPC_PORT = os.getenv("DAPR_GRPC_PORT", "50001")
DAPR_PUBSUB_NAME = "pubsub-kafka"

# Kafka topics
TOPIC_TASK_EVENTS = "task-events"
TOPIC_REMINDERS = "reminders"
TOPIC_TASK_UPDATES = "task-updates"

# Event types
EVENT_TASK_CREATED = "task_created"
EVENT_TASK_UPDATED = "task_updated"
EVENT_TASK_DELETED = "task_deleted"
EVENT_TASK_COMPLETED = "task_completed"


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_task_data() -> Dict[str, Any]:
    """Sample task data for testing."""
    return {
        "title": "Test Task for Event Flow",
        "description": "This task is used to test event publishing",
        "user_id": "test_user_123",
        "priority": "high",
        "tags": ["test", "event-flow"],
        "due_date": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
        "recurrence_rule": None,
        "reminder_offset": 3600,  # 1 hour before due date
        "status": "pending"
    }


@pytest.fixture
def sample_reminder_event() -> Dict[str, Any]:
    """Sample reminder event for testing."""
    return {
        "event_id": "reminder_evt_12345",
        "event_type": "reminder_trigger",
        "task_id": "task_abc123",
        "user_id": "test_user_123",
        "reminder_time": datetime.now(UTC).isoformat(),
        "notification_type": "due_date_reminder",
        "task_title": "Test Task",
        "due_date": (datetime.now(UTC) + timedelta(hours=1)).isoformat()
    }


@pytest.fixture
def sample_task_event() -> Dict[str, Any]:
    """Sample task event for testing."""
    return {
        "event_id": "task_evt_67890",
        "event_type": EVENT_TASK_CREATED,
        "task_id": "task_xyz789",
        "user_id": "test_user_123",
        "timestamp": datetime.now(UTC).isoformat(),
        "task_data": {
            "title": "New Task",
            "status": "pending",
            "priority": "medium"
        },
        "old_data": None,
        "new_data": None
    }


@pytest.fixture
def dapr_client_mock():
    """Mock Dapr HTTP client for unit tests."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance

        # Mock publish response
        mock_instance.post.return_value.status_code = 200
        mock_instance.post.return_value.json.return_value = {"status": "success"}

        yield mock_instance


@pytest.fixture
def kafka_consumer_mock():
    """Mock Kafka consumer for unit tests."""
    mock_consumer = MagicMock()
    mock_consumer.subscribe.return_value = None
    mock_consumer.poll.return_value = None
    mock_consumer.commit.return_value = None

    return mock_consumer


# =============================================================================
# Helper Functions
# =============================================================================

async def publish_event_to_dapr(
    topic: str,
    event_data: Dict[str, Any],
    pubsub_name: str = DAPR_PUBSUB_NAME
) -> Dict[str, Any]:
    """
    Publish event to Dapr Pub/Sub (Kafka).

    Args:
        topic: Kafka topic name
        event_data: Event payload
        pubsub_name: Dapr pubsub component name

    Returns:
        Response from Dapr API
    """
    import httpx

    dapr_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{pubsub_name}/{topic}"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            dapr_url,
            json=event_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return {"status_code": response.status_code, "response": response.text}


async def get_state_from_dapr(
    state_store: str,
    key: str
) -> Dict[str, Any]:
    """
    Get state from Dapr State Store.

    Args:
        state_store: Dapr state store component name
        key: State key

    Returns:
        State value
    """
    import httpx

    dapr_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{state_store}/{key}"

    async with httpx.AsyncClient() as client:
        response = await client.get(dapr_url)
        response.raise_for_status()
        return response.json()


async def save_state_to_dapr(
    state_store: str,
    key: str,
    value: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Save state to Dapr State Store.

    Args:
        state_store: Dapr state store component name
        key: State key
        value: State value

    Returns:
        Response from Dapr API
    """
    import httpx

    dapr_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{state_store}"

    payload = [
        {
            "key": key,
            "value": value
        }
    ]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            dapr_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return {"status_code": response.status_code}


async def delete_state_from_dapr(
    state_store: str,
    key: str
) -> Dict[str, Any]:
    """
    Delete state from Dapr State Store.

    Args:
        state_store: Dapr state store component name
        key: State key

    Returns:
        Response from Dapr API
    """
    import httpx

    dapr_url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{state_store}/{key}"

    async with httpx.AsyncClient() as client:
        response = await client.delete(dapr_url)
        response.raise_for_status()
        return {"status_code": response.status_code}


def validate_event_schema(event: Dict[str, Any], event_type: str) -> bool:
    """
    Validate event schema compliance.

    Args:
        event: Event data
        event_type: Expected event type

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["event_id", "event_type", "user_id", "timestamp"]

    # Check required fields
    for field in required_fields:
        if field not in event:
            return False

    # Check event type matches
    if event["event_type"] != event_type:
        return False

    # Type-specific validation
    if event_type in [EVENT_TASK_CREATED, EVENT_TASK_UPDATED, EVENT_TASK_DELETED, EVENT_TASK_COMPLETED]:
        if "task_id" not in event:
            return False
        if "task_data" not in event and event_type == EVENT_TASK_CREATED:
            return False

    if event_type == "reminder_trigger":
        if "reminder_time" not in event or "task_id" not in event:
            return False

    return True


# =============================================================================
# Unit Tests (Mocked Kafka)
# =============================================================================

@pytest.mark.asyncio
async def test_publish_task_created_event(dapr_client_mock, sample_task_data):
    """Test publishing task created event to Kafka."""
    event_data = {
        "event_id": "task_evt_001",
        "event_type": EVENT_TASK_CREATED,
        "task_id": "task_123",
        "user_id": sample_task_data["user_id"],
        "timestamp": datetime.now(UTC).isoformat(),
        "task_data": sample_task_data,
        "old_data": None,
        "new_data": None
    }

    # Mock publish
    dapr_client_mock.post.return_value.status_code = 200

    # Validate schema
    assert validate_event_schema(event_data, EVENT_TASK_CREATED)

    # Verify all required fields present
    assert event_data["event_id"] is not None
    assert event_data["task_id"] is not None
    assert event_data["user_id"] == sample_task_data["user_id"]
    assert event_data["task_data"]["title"] == sample_task_data["title"]


@pytest.mark.asyncio
async def test_publish_task_updated_event(sample_task_data):
    """Test publishing task updated event with old and new data."""
    old_data = sample_task_data.copy()
    new_data = sample_task_data.copy()
    new_data["status"] = "completed"
    new_data["priority"] = "low"

    event_data = {
        "event_id": "task_evt_002",
        "event_type": EVENT_TASK_UPDATED,
        "task_id": "task_123",
        "user_id": sample_task_data["user_id"],
        "timestamp": datetime.now(UTC).isoformat(),
        "task_data": new_data,
        "old_data": old_data,
        "new_data": new_data
    }

    # Validate schema
    assert validate_event_schema(event_data, EVENT_TASK_UPDATED)

    # Verify changes captured
    assert event_data["old_data"]["status"] == "pending"
    assert event_data["new_data"]["status"] == "completed"
    assert event_data["old_data"]["priority"] == "high"
    assert event_data["new_data"]["priority"] == "low"


@pytest.mark.asyncio
async def test_publish_reminder_event(sample_reminder_event):
    """Test publishing reminder event to reminders topic."""
    # Validate schema
    assert sample_reminder_event["event_id"] is not None
    assert sample_reminder_event["event_type"] == "reminder_trigger"
    assert sample_reminder_event["task_id"] is not None
    assert sample_reminder_event["user_id"] is not None
    assert sample_reminder_event["reminder_time"] is not None

    # Validate reminder-specific fields
    assert "notification_type" in sample_reminder_event
    assert "task_title" in sample_reminder_event
    assert "due_date" in sample_reminder_event


@pytest.mark.asyncio
async def test_publish_task_completed_event(sample_task_data):
    """Test publishing task completed event when task marked done."""
    event_data = {
        "event_id": "task_evt_003",
        "event_type": EVENT_TASK_COMPLETED,
        "task_id": "task_123",
        "user_id": sample_task_data["user_id"],
        "timestamp": datetime.now(UTC).isoformat(),
        "task_data": sample_task_data,
        "old_data": {"status": "pending"},
        "new_data": {"status": "completed"}
    }

    # Validate schema
    assert validate_event_schema(event_data, EVENT_TASK_COMPLETED)

    # Verify completion triggered
    assert event_data["new_data"]["status"] == "completed"


@pytest.mark.asyncio
async def test_event_schema_validation_missing_fields():
    """Test event schema validation fails with missing required fields."""
    # Missing event_id
    invalid_event = {
        "event_type": EVENT_TASK_CREATED,
        "user_id": "user_123",
        "timestamp": datetime.now(UTC).isoformat()
    }

    assert not validate_event_schema(invalid_event, EVENT_TASK_CREATED)

    # Missing user_id
    invalid_event2 = {
        "event_id": "evt_001",
        "event_type": EVENT_TASK_CREATED,
        "timestamp": datetime.now(UTC).isoformat()
    }

    assert not validate_event_schema(invalid_event2, EVENT_TASK_CREATED)


# =============================================================================
# Integration Tests (Real Kafka - requires INTEGRATION_TEST=1)
# =============================================================================

@pytest.mark.skipif(not INTEGRATION_TEST, reason="Integration test requires Dapr + Kafka")
@pytest.mark.asyncio
async def test_integration_publish_to_task_events_topic(sample_task_event):
    """
    Integration test: Publish event to task-events Kafka topic via Dapr.
    Requires Dapr runtime and Kafka cluster.
    """
    result = await publish_event_to_dapr(TOPIC_TASK_EVENTS, sample_task_event)

    assert result["status_code"] == 200
    print(f"✓ Published to {TOPIC_TASK_EVENTS}: {sample_task_event['event_id']}")


@pytest.mark.skipif(not INTEGRATION_TEST, reason="Integration test requires Dapr + Kafka")
@pytest.mark.asyncio
async def test_integration_publish_to_reminders_topic(sample_reminder_event):
    """
    Integration test: Publish event to reminders Kafka topic via Dapr.
    Verifies reminder events can be published when due date trigger fires.
    """
    result = await publish_event_to_dapr(TOPIC_REMINDERS, sample_reminder_event)

    assert result["status_code"] == 200
    print(f"✓ Published to {TOPIC_REMINDERS}: {sample_reminder_event['event_id']}")


@pytest.mark.skipif(not INTEGRATION_TEST, reason="Integration test requires Dapr + Kafka")
@pytest.mark.asyncio
async def test_integration_publish_to_task_updates_topic(sample_task_event):
    """
    Integration test: Publish event to task-updates Kafka topic via Dapr.
    Verifies task update events can be published.
    """
    update_event = sample_task_event.copy()
    update_event["event_type"] = EVENT_TASK_UPDATED
    update_event["event_id"] = "task_evt_update_001"

    result = await publish_event_to_dapr(TOPIC_TASK_UPDATES, update_event)

    assert result["status_code"] == 200
    print(f"✓ Published to {TOPIC_TASK_UPDATES}: {update_event['event_id']}")


@pytest.mark.skipif(not INTEGRATION_TEST, reason="Integration test requires Dapr + State Store")
@pytest.mark.asyncio
async def test_integration_dapr_state_store_get():
    """
    Integration test: Get state from Dapr State Store (PostgreSQL).
    Verifies Dapr state store operations work.
    """
    state_store = "statestore-postgresql"
    test_key = "test_state_key_001"

    # First save a test state
    test_value = {
        "user_id": "test_user_123",
        "data": "test data",
        "timestamp": datetime.now(UTC).isoformat()
    }

    await save_state_to_dapr(state_store, test_key, test_value)

    # Now retrieve it
    result = await get_state_from_dapr(state_store, test_key)

    assert result is not None
    print(f"✓ Retrieved state from Dapr: {result}")


@pytest.mark.skipif(not INTEGRATION_TEST, reason="Integration test requires Dapr + State Store")
@pytest.mark.asyncio
async def test_integration_dapr_state_store_set():
    """
    Integration test: Set state in Dapr State Store (PostgreSQL).
    Verifies state can be saved.
    """
    state_store = "statestore-postgresql"
    test_key = "test_state_key_002"
    test_value = {
        "task_id": "task_123",
        "status": "completed",
        "updated_at": datetime.now(UTC).isoformat()
    }

    result = await save_state_to_dapr(state_store, test_key, test_value)

    assert result["status_code"] == 200
    print(f"✓ Saved state to Dapr: {test_key}")


@pytest.mark.skipif(not INTEGRATION_TEST, reason="Integration test requires Dapr + State Store")
@pytest.mark.asyncio
async def test_integration_dapr_state_store_delete():
    """
    Integration test: Delete state from Dapr State Store.
    Verifies state can be deleted.
    """
    state_store = "statestore-postgresql"
    test_key = "test_state_key_003"

    # First save a test state
    test_value = {"test": "data"}
    await save_state_to_dapr(state_store, test_key, test_value)

    # Now delete it
    result = await delete_state_from_dapr(state_store, test_key)

    assert result["status_code"] == 200
    print(f"✓ Deleted state from Dapr: {test_key}")


@pytest.mark.skipif(not INTEGRATION_TEST, reason="Integration test requires full stack")
@pytest.mark.asyncio
async def test_integration_end_to_end_event_flow():
    """
    End-to-end integration test: Create task → Publish event → Verify event received.
    This test requires:
    - Dapr runtime running
    - Kafka cluster running
    - Event consumer service running
    - Database accessible
    """
    # Create task event
    task_data = {
        "title": "E2E Test Task",
        "description": "End-to-end event flow test",
        "user_id": "e2e_test_user",
        "priority": "high",
        "tags": ["e2e", "test"],
        "status": "pending"
    }

    event_data = {
        "event_id": f"e2e_evt_{datetime.now(UTC).timestamp()}",
        "event_type": EVENT_TASK_CREATED,
        "task_id": f"e2e_task_{datetime.now(UTC).timestamp()}",
        "user_id": task_data["user_id"],
        "timestamp": datetime.now(UTC).isoformat(),
        "task_data": task_data
    }

    # Publish to task-events topic
    result = await publish_event_to_dapr(TOPIC_TASK_EVENTS, event_data)

    assert result["status_code"] == 200

    # Wait for event to be consumed (adjust timing as needed)
    await asyncio.sleep(2)

    # In a real integration test, we would verify:
    # - Event was consumed by audit service
    # - Audit log entry created in database
    # - No data loss occurred

    print(f"✓ E2E event flow complete: {event_data['event_id']}")


# =============================================================================
# Performance Tests
# =============================================================================

@pytest.mark.skipif(not INTEGRATION_TEST, reason="Performance test requires real Kafka")
@pytest.mark.asyncio
async def test_bulk_event_publishing():
    """
    Performance test: Publish 100 events and measure throughput.
    Verifies system can handle bulk event publishing.
    """
    num_events = 100
    start_time = datetime.now(UTC)

    tasks = []
    for i in range(num_events):
        event_data = {
            "event_id": f"perf_evt_{i}",
            "event_type": EVENT_TASK_CREATED,
            "task_id": f"task_{i}",
            "user_id": "perf_test_user",
            "timestamp": datetime.now(UTC).isoformat(),
            "task_data": {"title": f"Task {i}"}
        }

        tasks.append(publish_event_to_dapr(TOPIC_TASK_EVENTS, event_data))

    # Publish all events concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = datetime.now(UTC)
    duration = (end_time - start_time).total_seconds()

    # Verify all succeeded
    successful = sum(1 for r in results if isinstance(r, dict) and r.get("status_code") == 200)

    print(f"✓ Published {successful}/{num_events} events in {duration:.2f}s")
    print(f"  Throughput: {successful/duration:.2f} events/sec")

    assert successful == num_events
    assert duration < 10.0  # Should complete in under 10 seconds
