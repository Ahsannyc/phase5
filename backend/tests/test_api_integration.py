"""Integration tests for Task API with Phase 5 Part A extensions."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, SQLModel
from app.main import app
from app.database import get_session
from app.models.user import User


# Test database setup
@pytest.fixture(scope="function")
def test_db():
    """Create test database."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with database override."""
    def get_test_db():
        yield test_db

    app.dependency_overrides[get_session] = get_test_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(test_db):
    """Create authenticated user and return auth headers."""
    # Create test user
    user = User(id=1, email="test@example.com", username="testuser")
    test_db.add(user)
    test_db.commit()

    # Mock JWT token (in real tests, generate proper token)
    token = "test_jwt_token"
    return {"Authorization": f"Bearer {token}"}


class TestPriorityFeature:
    """Integration tests for priority feature."""

    def test_create_task_with_priority(self, client, auth_headers):
        """Test creating task with priority via POST."""
        task_data = {
            "title": "High Priority Task",
            "priority": "high"
        }
        response = client.post("/api/1/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == "high"

    def test_get_tasks_returns_priority(self, client, auth_headers):
        """Test GET /tasks returns priority field."""
        # Create task first
        task_data = {"title": "Task", "priority": "medium"}
        client.post("/api/1/tasks", json=task_data, headers=auth_headers)

        # Get tasks
        response = client.get("/api/1/tasks", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) > 0
        assert "priority" in tasks[0]

    def test_filter_by_priority_high(self, client, auth_headers):
        """Test filtering tasks by high priority."""
        # Create tasks with different priorities
        client.post("/api/1/tasks", json={"title": "Low Task", "priority": "low"}, headers=auth_headers)
        client.post("/api/1/tasks", json={"title": "High Task", "priority": "high"}, headers=auth_headers)

        # Filter by high priority
        response = client.get("/api/1/tasks?priority=high", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["priority"] == "high"

    def test_sort_by_priority(self, client, auth_headers):
        """Test sorting tasks by priority."""
        # Create tasks in random order
        priorities = ["high", "low", "medium"]
        for p in priorities:
            client.post("/api/1/tasks", json={"title": f"{p} task", "priority": p}, headers=auth_headers)

        # Sort by priority ascending
        response = client.get("/api/1/tasks?sort=priority", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        priorities_sorted = [t["priority"] for t in tasks]
        # Alphabetical: high, low, medium
        assert priorities_sorted == ["high", "low", "medium"]

    def test_multi_filter_priority_and_status(self, client, auth_headers):
        """Test combining priority filter with status filter."""
        # Create tasks
        client.post("/api/1/tasks", json={"title": "Task 1", "priority": "high", "completed": False}, headers=auth_headers)
        client.post("/api/1/tasks", json={"title": "Task 2", "priority": "high", "completed": True}, headers=auth_headers)
        client.post("/api/1/tasks", json={"title": "Task 3", "priority": "low", "completed": False}, headers=auth_headers)

        # Filter: priority=high AND status=pending
        response = client.get("/api/1/tasks?priority=high&status=pending", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["priority"] == "high"
        assert tasks[0]["completed"] == False


class TestTagsFeature:
    """Integration tests for tags feature."""

    def test_create_task_with_tags(self, client, auth_headers):
        """Test creating task with tags via POST."""
        task_data = {
            "title": "Tagged Task",
            "tags": ["work", "urgent"]
        }
        response = client.post("/api/1/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["tags"] == ["work", "urgent"]

    def test_filter_by_single_tag(self, client, auth_headers):
        """Test filtering tasks by single tag."""
        client.post("/api/1/tasks", json={"title": "Work Task", "tags": ["work"]}, headers=auth_headers)
        client.post("/api/1/tasks", json={"title": "Personal Task", "tags": ["personal"]}, headers=auth_headers)

        response = client.get("/api/1/tasks?tag=work", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert "work" in tasks[0]["tags"]

    def test_filter_by_multiple_tags_or_logic(self, client, auth_headers):
        """Test filtering by multiple tags uses OR logic."""
        client.post("/api/1/tasks", json={"title": "Task 1", "tags": ["work"]}, headers=auth_headers)
        client.post("/api/1/tasks", json={"title": "Task 2", "tags": ["personal"]}, headers=auth_headers)
        client.post("/api/1/tasks", json={"title": "Task 3", "tags": ["urgent"]}, headers=auth_headers)

        response = client.get("/api/1/tasks?tag=work&tag=personal", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        # Should return tasks with either work OR personal tag
        assert len(tasks) >= 2

    def test_combined_priority_and_tag_filter(self, client, auth_headers):
        """Test combining priority and tag filters (AND logic)."""
        client.post("/api/1/tasks", json={"title": "Task 1", "priority": "high", "tags": ["work"]}, headers=auth_headers)
        client.post("/api/1/tasks", json={"title": "Task 2", "priority": "high", "tags": ["personal"]}, headers=auth_headers)
        client.post("/api/1/tasks", json={"title": "Task 3", "priority": "low", "tags": ["work"]}, headers=auth_headers)

        response = client.get("/api/1/tasks?priority=high&tag=work", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["priority"] == "high"
        assert "work" in tasks[0]["tags"]


class TestSearchFeature:
    """Integration tests for search feature."""

    def test_search_by_title(self, client, auth_headers):
        """Test searching tasks by title."""
        client.post("/api/1/tasks", json={"title": "Budget Planning Q1"}, headers=auth_headers)
        client.post("/api/1/tasks", json={"title": "Team Meeting"}, headers=auth_headers)

        response = client.get("/api/1/tasks?search=budget", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert "Budget" in tasks[0]["title"]

    def test_search_by_description(self, client, auth_headers):
        """Test searching tasks by description."""
        client.post("/api/1/tasks", json={
            "title": "Task",
            "description": "Review quarterly budget"
        }, headers=auth_headers)

        response = client.get("/api/1/tasks?search=budget", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1

    def test_search_case_insensitive(self, client, auth_headers):
        """Test search is case-insensitive."""
        client.post("/api/1/tasks", json={"title": "Budget Planning"}, headers=auth_headers)

        # Search with uppercase
        response = client.get("/api/1/tasks?search=BUDGET", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1

        # Search with lowercase
        response = client.get("/api/1/tasks?search=budget", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1

    def test_search_partial_match(self, client, auth_headers):
        """Test search matches partial words."""
        client.post("/api/1/tasks", json={"title": "Meeting with team"}, headers=auth_headers)

        response = client.get("/api/1/tasks?search=meet", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1

    def test_search_no_results(self, client, auth_headers):
        """Test search with no matching results."""
        client.post("/api/1/tasks", json={"title": "Task"}, headers=auth_headers)

        response = client.get("/api/1/tasks?search=nonexistent", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 0


class TestFilterFeature:
    """Integration tests for advanced filtering."""

    def test_combined_filters_and_logic(self, client, auth_headers):
        """Test multiple filters combine with AND logic."""
        # Create diverse tasks
        client.post("/api/1/tasks", json={
            "title": "Task 1",
            "priority": "high",
            "tags": ["work"],
            "completed": False
        }, headers=auth_headers)
        client.post("/api/1/tasks", json={
            "title": "Task 2",
            "priority": "high",
            "tags": ["personal"],
            "completed": False
        }, headers=auth_headers)
        client.post("/api/1/tasks", json={
            "title": "Task 3",
            "priority": "low",
            "tags": ["work"],
            "completed": False
        }, headers=auth_headers)

        # Apply filters: status=pending AND priority=high AND tag=work
        response = client.get("/api/1/tasks?status=pending&priority=high&tag=work", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Task 1"

    def test_filter_matching_zero_tasks(self, client, auth_headers):
        """Test filter with no matching tasks returns empty list."""
        client.post("/api/1/tasks", json={"title": "Task", "priority": "low"}, headers=auth_headers)

        response = client.get("/api/1/tasks?priority=high", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 0


class TestSortFeature:
    """Integration tests for sorting."""

    def test_sort_by_due_date_ascending(self, client, auth_headers):
        """Test sorting by due_date ascending (earliest first)."""
        dates = [
            (datetime.utcnow() + timedelta(days=3)).isoformat(),
            (datetime.utcnow() + timedelta(days=1)).isoformat(),
            (datetime.utcnow() + timedelta(days=2)).isoformat()
        ]
        for i, date in enumerate(dates):
            client.post("/api/1/tasks", json={"title": f"Task {i}", "due_date": date}, headers=auth_headers)

        response = client.get("/api/1/tasks?sort=due_date", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        # Verify ascending order
        due_dates = [t["due_date"] for t in tasks if t["due_date"]]
        assert due_dates[0] < due_dates[1] < due_dates[2]

    def test_sort_with_filters(self, client, auth_headers):
        """Test sorting applies to filtered results."""
        # Create tasks with different priorities
        for priority in ["high", "medium", "low"]:
            client.post("/api/1/tasks", json={
                "title": f"{priority} work task",
                "priority": priority,
                "tags": ["work"]
            }, headers=auth_headers)

        # Filter by tag=work and sort by priority
        response = client.get("/api/1/tasks?tag=work&sort=priority", headers=auth_headers)
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 3
        priorities = [t["priority"] for t in tasks]
        assert priorities == ["high", "low", "medium"]  # Alphabetical


class TestRecurringTasks:
    """Integration tests for recurring tasks."""

    def test_create_recurring_task(self, client, auth_headers):
        """Test creating recurring task via POST."""
        task_data = {
            "title": "Daily Standup",
            "recurrence_rule": "daily",
            "due_date": datetime.utcnow().isoformat()
        }
        response = client.post("/api/1/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["recurrence_rule"] == "daily"

    def test_complete_recurring_task_creates_next_instance(self, client, auth_headers):
        """Test that marking recurring task complete creates next instance."""
        # Create recurring task
        task_data = {
            "title": "Daily Standup",
            "recurrence_rule": "daily",
            "due_date": datetime.utcnow().isoformat()
        }
        response = client.post("/api/1/tasks", json=task_data, headers=auth_headers)
        task_id = response.json()["id"]

        # Mark complete
        response = client.patch(f"/api/1/tasks/{task_id}/complete", json={"completed": True}, headers=auth_headers)
        assert response.status_code == 200

        # Verify next instance created
        response = client.get("/api/1/tasks", headers=auth_headers)
        tasks = response.json()
        assert len(tasks) == 2  # Original + next instance

        # Find next instance (not completed)
        next_instance = [t for t in tasks if not t["completed"]][0]
        assert next_instance["title"] == "Daily Standup"
        assert next_instance["recurrence_rule"] == "daily"

    def test_next_instance_inherits_properties(self, client, auth_headers):
        """Test next instance inherits title, priority, tags, recurrence, reminder."""
        task_data = {
            "title": "Weekly Review",
            "description": "Review tasks",
            "priority": "high",
            "tags": ["work", "planning"],
            "recurrence_rule": "weekly",
            "due_date": datetime.utcnow().isoformat(),
            "reminder_offset": 24
        }
        response = client.post("/api/1/tasks", json=task_data, headers=auth_headers)
        task_id = response.json()["id"]

        # Mark complete
        client.patch(f"/api/1/tasks/{task_id}/complete", json={"completed": True}, headers=auth_headers)

        # Get next instance
        response = client.get("/api/1/tasks?status=pending", headers=auth_headers)
        tasks = response.json()
        next_instance = tasks[0]

        assert next_instance["title"] == "Weekly Review"
        assert next_instance["description"] == "Review tasks"
        assert next_instance["priority"] == "high"
        assert next_instance["tags"] == ["work", "planning"]
        assert next_instance["recurrence_rule"] == "weekly"
        assert next_instance["reminder_offset"] == 24


class TestDueDatesAndReminders:
    """Integration tests for due dates and reminders."""

    def test_create_task_with_due_date(self, client, auth_headers):
        """Test creating task with due date."""
        due_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
        task_data = {
            "title": "Task with Due Date",
            "due_date": due_date
        }
        response = client.post("/api/1/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["due_date"] is not None

    def test_overdue_task_marked(self, client, auth_headers):
        """Test that overdue tasks are marked correctly."""
        # Create overdue task
        past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
        task_data = {
            "title": "Overdue Task",
            "due_date": past_date,
            "completed": False
        }
        response = client.post("/api/1/tasks", json=task_data, headers=auth_headers)
        task_id = response.json()["id"]

        # Get task
        response = client.get(f"/api/1/tasks/{task_id}", headers=auth_headers)
        data = response.json()
        assert data["is_overdue"] == True

    def test_completed_task_not_overdue(self, client, auth_headers):
        """Test that completed tasks are not marked overdue."""
        past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
        task_data = {
            "title": "Completed Overdue Task",
            "due_date": past_date,
            "completed": True
        }
        response = client.post("/api/1/tasks", json=task_data, headers=auth_headers)
        data = response.json()
        assert data["is_overdue"] == False

    def test_create_task_with_reminder(self, client, auth_headers):
        """Test creating task with reminder offset."""
        task_data = {
            "title": "Task with Reminder",
            "due_date": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "reminder_offset": 24
        }
        response = client.post("/api/1/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["reminder_offset"] == 24


class TestMultiUserIsolation:
    """Integration tests for multi-user isolation."""

    def test_user_cannot_see_other_users_tasks(self, client, test_db):
        """Test that User A cannot see User B's tasks."""
        # Create two users
        user1 = User(id=1, email="user1@example.com", username="user1")
        user2 = User(id=2, email="user2@example.com", username="user2")
        test_db.add(user1)
        test_db.add(user2)
        test_db.commit()

        # User 1 creates high priority task
        headers1 = {"Authorization": "Bearer user1_token"}
        client.post("/api/1/tasks", json={"title": "User 1 Task", "priority": "high"}, headers=headers1)

        # User 2 cannot see User 1's task
        headers2 = {"Authorization": "Bearer user2_token"}
        response = client.get("/api/2/tasks", headers=headers2)
        tasks = response.json()
        assert len(tasks) == 0

    def test_filter_isolation(self, client, test_db):
        """Test that filtering respects user isolation."""
        user1 = User(id=1, email="user1@example.com", username="user1")
        user2 = User(id=2, email="user2@example.com", username="user2")
        test_db.add(user1)
        test_db.add(user2)
        test_db.commit()

        headers1 = {"Authorization": "Bearer user1_token"}
        headers2 = {"Authorization": "Bearer user2_token"}

        # Both users create high priority tasks
        client.post("/api/1/tasks", json={"title": "User 1 High", "priority": "high"}, headers=headers1)
        client.post("/api/2/tasks", json={"title": "User 2 High", "priority": "high"}, headers=headers2)

        # User 1 filters by high priority
        response = client.get("/api/1/tasks?priority=high", headers=headers1)
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "User 1 High"


class TestErrorHandling:
    """Integration tests for error handling."""

    def test_invalid_priority_returns_422(self, client, auth_headers):
        """Test invalid priority returns 422 validation error."""
        task_data = {
            "title": "Invalid Task",
            "priority": "urgent"  # Invalid value
        }
        response = client.post("/api/1/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 422

    def test_too_many_tags_returns_422(self, client, auth_headers):
        """Test too many tags returns 422 validation error."""
        task_data = {
            "title": "Too Many Tags",
            "tags": [f"tag{i}" for i in range(21)]  # 21 tags, max is 20
        }
        response = client.post("/api/1/tasks", json=task_data, headers=auth_headers)
        assert response.status_code == 422

    def test_task_not_found_returns_404(self, client, auth_headers):
        """Test accessing non-existent task returns 404."""
        response = client.get("/api/1/tasks/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_unauthorized_access_returns_401(self, client):
        """Test accessing without auth returns 401."""
        response = client.get("/api/1/tasks")
        # Depending on auth implementation, may be 401 or 403
        assert response.status_code in [401, 403]
