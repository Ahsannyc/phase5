"""Unit tests for Task models with Phase 5 Part A extensions."""

import pytest
from datetime import datetime, timedelta
from app.models.task import Task, TaskPriority, TaskStatus


class TestTaskPriorityEnum:
    """Test TaskPriority enum values."""

    def test_priority_enum_values(self):
        """Test that TaskPriority enum has correct values."""
        assert TaskPriority.LOW == "low"
        assert TaskPriority.MEDIUM == "medium"
        assert TaskPriority.HIGH == "high"

    def test_priority_enum_members(self):
        """Test that TaskPriority enum has exactly 3 members."""
        assert len(TaskPriority) == 3


class TestTaskStatusEnum:
    """Test TaskStatus enum values."""

    def test_status_enum_values(self):
        """Test that TaskStatus enum has correct values."""
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.COMPLETED == "completed"

    def test_status_enum_members(self):
        """Test that TaskStatus enum has exactly 2 members."""
        assert len(TaskStatus) == 2


class TestTaskModel:
    """Test Task model fields and properties."""

    def test_task_default_values(self):
        """Test that Task model has correct default values."""
        task = Task(
            title="Test Task",
            user_id=1
        )
        assert task.completed == False
        assert task.priority == "medium"
        assert task.tags == []
        assert task.due_date is None
        assert task.recurrence_rule is None
        assert task.reminder_offset is None

    def test_task_with_priority(self):
        """Test creating task with priority."""
        task = Task(
            title="High Priority Task",
            user_id=1,
            priority="high"
        )
        assert task.priority == "high"

    def test_task_with_tags(self):
        """Test creating task with tags."""
        task = Task(
            title="Tagged Task",
            user_id=1,
            tags=["work", "urgent"]
        )
        assert task.tags == ["work", "urgent"]

    def test_task_with_due_date(self):
        """Test creating task with due date."""
        due_date = datetime.utcnow() + timedelta(days=1)
        task = Task(
            title="Task with Due Date",
            user_id=1,
            due_date=due_date
        )
        assert task.due_date == due_date

    def test_task_with_recurrence(self):
        """Test creating task with recurrence rule."""
        task = Task(
            title="Recurring Task",
            user_id=1,
            recurrence_rule="daily"
        )
        assert task.recurrence_rule == "daily"

    def test_task_with_reminder(self):
        """Test creating task with reminder offset."""
        task = Task(
            title="Task with Reminder",
            user_id=1,
            reminder_offset=24
        )
        assert task.reminder_offset == 24


class TestTaskComputedProperties:
    """Test Task model computed properties."""

    def test_is_overdue_false_no_due_date(self):
        """Test is_overdue returns False when no due date."""
        task = Task(
            title="No Due Date",
            user_id=1,
            completed=False
        )
        assert task.is_overdue == False

    def test_is_overdue_false_when_completed(self):
        """Test is_overdue returns False when task is completed."""
        task = Task(
            title="Completed Task",
            user_id=1,
            due_date=datetime.utcnow() - timedelta(days=1),
            completed=True
        )
        assert task.is_overdue == False

    def test_is_overdue_true_when_past_due(self):
        """Test is_overdue returns True when due_date < now AND not completed."""
        task = Task(
            title="Overdue Task",
            user_id=1,
            due_date=datetime.utcnow() - timedelta(days=1),
            completed=False
        )
        assert task.is_overdue == True

    def test_is_overdue_false_when_future_due_date(self):
        """Test is_overdue returns False when due date is in future."""
        task = Task(
            title="Future Task",
            user_id=1,
            due_date=datetime.utcnow() + timedelta(days=1),
            completed=False
        )
        assert task.is_overdue == False

    def test_reminder_datetime_none_when_no_due_date(self):
        """Test reminder_datetime returns None when no due date."""
        task = Task(
            title="No Due Date",
            user_id=1,
            reminder_offset=24
        )
        assert task.reminder_datetime is None

    def test_reminder_datetime_none_when_no_offset(self):
        """Test reminder_datetime returns None when no reminder offset."""
        task = Task(
            title="No Reminder",
            user_id=1,
            due_date=datetime.utcnow() + timedelta(days=1)
        )
        assert task.reminder_datetime is None

    def test_reminder_datetime_calculated_correctly(self):
        """Test reminder_datetime calculates correctly (due_date - offset hours)."""
        due_date = datetime.utcnow() + timedelta(days=2)
        task = Task(
            title="Task with Reminder",
            user_id=1,
            due_date=due_date,
            reminder_offset=24  # 24 hours = 1 day
        )
        expected_reminder = due_date - timedelta(hours=24)
        assert task.reminder_datetime == expected_reminder


class TestTaskFieldValidation:
    """Test Task model field validation."""

    def test_priority_accepts_valid_values(self):
        """Test that priority accepts low, medium, high."""
        for priority in ["low", "medium", "high"]:
            task = Task(
                title=f"{priority} task",
                user_id=1,
                priority=priority
            )
            assert task.priority == priority

    def test_tags_accepts_empty_list(self):
        """Test that tags accepts empty list."""
        task = Task(
            title="No Tags",
            user_id=1,
            tags=[]
        )
        assert task.tags == []

    def test_tags_accepts_multiple_tags(self):
        """Test that tags accepts multiple tags."""
        tags = ["work", "personal", "urgent", "important"]
        task = Task(
            title="Many Tags",
            user_id=1,
            tags=tags
        )
        assert task.tags == tags
