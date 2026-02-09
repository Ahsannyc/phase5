"""Unit tests for Task schemas with Phase 5 Part A validation."""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse


class TestTaskCreateSchema:
    """Test TaskCreate schema validation."""

    def test_task_create_with_valid_data(self):
        """Test creating TaskCreate with all valid fields."""
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "completed": False,
            "priority": "high",
            "tags": ["work", "urgent"],
            "due_date": datetime.utcnow() + timedelta(days=1),
            "recurrence_rule": "daily",
            "reminder_offset": 24
        }
        task = TaskCreate(**task_data)
        assert task.title == "Test Task"
        assert task.priority == "high"
        assert task.tags == ["work", "urgent"]

    def test_task_create_default_values(self):
        """Test TaskCreate default values."""
        task = TaskCreate(title="Minimal Task")
        assert task.completed == False
        assert task.priority == "medium"
        assert task.tags == []
        assert task.due_date is None
        assert task.recurrence_rule is None
        assert task.reminder_offset is None


class TestPriorityValidation:
    """Test priority field validation."""

    def test_priority_valid_low(self):
        """Test priority accepts 'low'."""
        task = TaskCreate(title="Low Priority", priority="low")
        assert task.priority == "low"

    def test_priority_valid_medium(self):
        """Test priority accepts 'medium'."""
        task = TaskCreate(title="Medium Priority", priority="medium")
        assert task.priority == "medium"

    def test_priority_valid_high(self):
        """Test priority accepts 'high'."""
        task = TaskCreate(title="High Priority", priority="high")
        assert task.priority == "high"

    def test_priority_rejects_invalid_value(self):
        """Test priority rejects invalid values."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Invalid Priority", priority="urgent")
        assert "Priority must be one of: low, medium, high" in str(exc_info.value)

    def test_priority_rejects_empty_string(self):
        """Test priority rejects empty string."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Empty Priority", priority="")
        assert "Priority must be one of: low, medium, high" in str(exc_info.value)


class TestTagsValidation:
    """Test tags field validation."""

    def test_tags_accepts_empty_list(self):
        """Test tags accepts empty list."""
        task = TaskCreate(title="No Tags", tags=[])
        assert task.tags == []

    def test_tags_accepts_single_tag(self):
        """Test tags accepts single tag."""
        task = TaskCreate(title="One Tag", tags=["work"])
        assert task.tags == ["work"]

    def test_tags_accepts_multiple_tags(self):
        """Test tags accepts multiple tags."""
        task = TaskCreate(title="Many Tags", tags=["work", "personal", "urgent"])
        assert task.tags == ["work", "personal", "urgent"]

    def test_tags_rejects_empty_tag(self):
        """Test tags rejects empty tag."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Empty Tag", tags=["work", "", "urgent"])
        assert "Each tag must be 1-50 characters" in str(exc_info.value)

    def test_tags_rejects_too_long_tag(self):
        """Test tags rejects tag longer than 50 characters."""
        long_tag = "a" * 51
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Long Tag", tags=[long_tag])
        assert "Each tag must be 1-50 characters" in str(exc_info.value)

    def test_tags_accepts_max_length_tag(self):
        """Test tags accepts tag with exactly 50 characters."""
        max_tag = "a" * 50
        task = TaskCreate(title="Max Tag", tags=[max_tag])
        assert task.tags == [max_tag]

    def test_tags_rejects_too_many_tags(self):
        """Test tags rejects more than 20 tags."""
        many_tags = [f"tag{i}" for i in range(21)]
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Too Many Tags", tags=many_tags)
        assert "Maximum 20 tags allowed" in str(exc_info.value)

    def test_tags_accepts_exactly_20_tags(self):
        """Test tags accepts exactly 20 tags."""
        exactly_20_tags = [f"tag{i}" for i in range(20)]
        task = TaskCreate(title="20 Tags", tags=exactly_20_tags)
        assert len(task.tags) == 20


class TestReminderOffsetValidation:
    """Test reminder_offset field validation."""

    def test_reminder_offset_accepts_none(self):
        """Test reminder_offset accepts None."""
        task = TaskCreate(title="No Reminder", reminder_offset=None)
        assert task.reminder_offset is None

    def test_reminder_offset_accepts_zero(self):
        """Test reminder_offset accepts 0."""
        task = TaskCreate(title="Zero Reminder", reminder_offset=0)
        assert task.reminder_offset == 0

    def test_reminder_offset_accepts_valid_value(self):
        """Test reminder_offset accepts valid value."""
        task = TaskCreate(title="Valid Reminder", reminder_offset=24)
        assert task.reminder_offset == 24

    def test_reminder_offset_accepts_max_value(self):
        """Test reminder_offset accepts max value (10080 hours = 7 days)."""
        task = TaskCreate(title="Max Reminder", reminder_offset=10080)
        assert task.reminder_offset == 10080

    def test_reminder_offset_rejects_negative(self):
        """Test reminder_offset rejects negative values."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Negative Reminder", reminder_offset=-1)
        assert "Reminder offset must be non-negative" in str(exc_info.value)

    def test_reminder_offset_rejects_too_large(self):
        """Test reminder_offset rejects values > 10080 hours."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Large Reminder", reminder_offset=10081)
        assert "Reminder offset must be <= 10080 hours (7 days)" in str(exc_info.value)


class TestTaskUpdateSchema:
    """Test TaskUpdate schema validation."""

    def test_task_update_all_fields_optional(self):
        """Test TaskUpdate allows all fields to be optional."""
        task = TaskUpdate()
        assert task.title is None
        assert task.description is None
        assert task.completed is None
        assert task.priority is None
        assert task.tags is None

    def test_task_update_partial_update(self):
        """Test TaskUpdate allows partial updates."""
        task = TaskUpdate(priority="high", tags=["urgent"])
        assert task.priority == "high"
        assert task.tags == ["urgent"]
        assert task.title is None

    def test_task_update_priority_validation(self):
        """Test TaskUpdate validates priority if provided."""
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(priority="invalid")
        assert "Priority must be one of: low, medium, high" in str(exc_info.value)

    def test_task_update_tags_validation(self):
        """Test TaskUpdate validates tags if provided."""
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(tags=["a" * 51])
        assert "Each tag must be 1-50 characters" in str(exc_info.value)

    def test_task_update_reminder_offset_validation(self):
        """Test TaskUpdate validates reminder_offset if provided."""
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(reminder_offset=-5)
        assert "Reminder offset must be non-negative" in str(exc_info.value)


class TestTaskResponseSchema:
    """Test TaskResponse schema."""

    def test_task_response_includes_all_fields(self):
        """Test TaskResponse includes all required fields."""
        task_data = {
            "id": 1,
            "user_id": 1,
            "title": "Test Task",
            "description": "Test Description",
            "completed": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "priority": "high",
            "tags": ["work"],
            "due_date": datetime.utcnow() + timedelta(days=1),
            "recurrence_rule": "daily",
            "reminder_offset": 24,
            "is_overdue": False
        }
        task = TaskResponse(**task_data)
        assert task.id == 1
        assert task.priority == "high"
        assert task.tags == ["work"]
        assert task.is_overdue == False
