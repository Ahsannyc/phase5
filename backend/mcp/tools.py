"""MCP Tools for Todo task management."""

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.task import Task, TaskCreate, TaskUpdate
from app.crud.task import (
    create_task as crud_create_task,
    get_task_by_id_and_user as crud_get_task,
    get_tasks_by_user as crud_get_tasks,
    update_task as crud_update_task,
    delete_task as crud_delete_task,
    toggle_task_completion as crud_toggle_task,
)
from typing import Optional, Any


class TodoTools:
    """Tools for managing Todo tasks via MCP."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_task(
        self,
        user_id: int,
        title: str,
        description: str = None,
        priority: str = "medium",
        tags: list = None,
        due_date: str = None,
        recurrence_rule: str = None,
        reminder_offset: int = None
    ) -> dict:
        """Add a new task for the user with Phase 5 Part A fields.

        Args:
            user_id: User ID
            title: Task title (required)
            description: Task description (optional)
            priority: Priority level - "low", "medium", or "high" (default: "medium")
            tags: List of tags (default: [])
            due_date: Due date in ISO 8601 format (default: None)
            recurrence_rule: Recurrence pattern like "daily", "weekly:monday", etc. (default: None)
            reminder_offset: Reminder offset in hours before due date (default: None)
        """
        try:
            # Validate priority
            if priority not in ["low", "medium", "high"]:
                return {
                    "success": False,
                    "message": f"❌ Invalid priority '{priority}'. Must be 'low', 'medium', or 'high'.",
                }

            # Validate tags
            if tags is None:
                tags = []
            if len(tags) > 20:
                return {
                    "success": False,
                    "message": "❌ Maximum 20 tags allowed.",
                }
            for tag in tags:
                if not tag or len(tag) > 50:
                    return {
                        "success": False,
                        "message": "❌ Each tag must be 1-50 characters.",
                    }

            # Validate reminder_offset
            if reminder_offset is not None:
                if reminder_offset < 0 or reminder_offset > 10080:
                    return {
                        "success": False,
                        "message": "❌ Reminder offset must be between 0 and 10080 hours (7 days).",
                    }

            # Parse due_date if provided
            from datetime import datetime
            parsed_due_date = None
            if due_date:
                try:
                    parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    if parsed_due_date < datetime.now(parsed_due_date.tzinfo):
                        return {
                            "success": False,
                            "message": "❌ Due date cannot be in the past.",
                        }
                except ValueError:
                    return {
                        "success": False,
                        "message": f"❌ Invalid due date format. Expected ISO 8601, got: {due_date}",
                    }

            task_create = TaskCreate(
                title=title,
                description=description,
                priority=priority,
                tags=tags,
                due_date=parsed_due_date,
                recurrence_rule=recurrence_rule,
                reminder_offset=reminder_offset
            )
            task = await self.db.run_sync(lambda s: crud_create_task(s, task_create, user_id))

            return {
                "success": True,
                "message": f"✅ Task '{title}' has been created successfully.",
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority,
                    "tags": task.tags,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "recurrence_rule": task.recurrence_rule,
                    "reminder_offset": task.reminder_offset,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error creating task: {str(e)}",
            }

    async def list_tasks(
        self,
        user_id: int,
        completed_only: bool = False,
        priority: str = None,
        tags: list = None,
        search: str = None,
        status: str = None,
        sort_by: str = "created_at",
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """List tasks for the user with Phase 5 Part A filtering and sorting.

        Args:
            user_id: User ID
            completed_only: Show only completed tasks (legacy, overridden by status if provided)
            priority: Filter by priority ("low", "medium", "high")
            tags: Filter by tags (list of tag names, OR logic)
            search: Search term for title/description
            status: Filter by status ("pending", "completed", "overdue")
            sort_by: Sort field ("-created_at", "due_date", "priority", "-priority", "title", etc.)
            page: Page number (default: 1)
            page_size: Items per page (default: 20)
        """
        try:
            # Validate priority if provided
            if priority and priority not in ["low", "medium", "high"]:
                return {
                    "success": False,
                    "message": f"❌ Invalid priority '{priority}'. Must be 'low', 'medium', or 'high'.",
                }

            # Validate status if provided
            if status and status not in ["pending", "completed", "overdue"]:
                return {
                    "success": False,
                    "message": f"❌ Invalid status '{status}'. Must be 'pending', 'completed', or 'overdue'.",
                }

            # Legacy support: map completed_only to status
            if completed_only and not status:
                status = "completed"

            # Call CRUD with filters
            from app.crud.task import get_tasks_by_user as crud_get_tasks_by_user
            tasks = await self.db.run_sync(
                lambda s: crud_get_tasks_by_user(
                    s,
                    user_id,
                    priority=priority,
                    tags=tags,
                    status=status,
                    search=search,
                    sort_by=sort_by,
                    page=page,
                    page_size=page_size
                )
            )

            if not tasks:
                filters_applied = any([priority, tags, search, status])
                message = "📋 No tasks match your filters." if filters_applied else "📋 You have no tasks yet. Create one with 'add task [name]'!"
                return {
                    "success": True,
                    "message": message,
                    "tasks": [],
                }

            # Build task list with new fields
            from datetime import datetime
            task_list = "\n".join([
                f"{'✅' if t.completed else '🔥' if (t.due_date and not t.completed and t.due_date < datetime.utcnow()) else '⭕'} " +
                f"[{t.priority.upper()}] Task {t.id}: {t.title}" +
                (f" - {t.description}" if t.description else "") +
                (f" | Tags: {', '.join(t.tags)}" if t.tags else "") +
                (f" | Due: {t.due_date.strftime('%Y-%m-%d %H:%M UTC')}" if t.due_date else "")
                for t in tasks
            ])

            return {
                "success": True,
                "message": f"📋 Here are your {len(tasks)} task(s):\n{task_list}",
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "description": t.description,
                        "completed": t.completed,
                        "priority": t.priority,
                        "tags": t.tags,
                        "due_date": t.due_date.isoformat() if t.due_date else None,
                        "recurrence_rule": t.recurrence_rule,
                        "reminder_offset": t.reminder_offset,
                        "is_overdue": t.due_date and not t.completed and t.due_date < datetime.utcnow(),
                    }
                    for t in tasks
                ],
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error listing tasks: {str(e)}",
            }

    async def update_task(
        self,
        user_id: int,
        task_id: int,
        title: str = None,
        description: str = None,
        completed: bool = None,
        priority: str = None,
        tags: list = None,
        due_date: str = None,
        recurrence_rule: str = None,
        reminder_offset: int = None
    ) -> dict:
        """Update a task for the user with Phase 5 Part A fields.

        Args:
            user_id: User ID
            task_id: Task ID to update
            title: New title (optional)
            description: New description (optional)
            completed: New completion status (optional)
            priority: New priority ("low", "medium", "high") (optional)
            tags: New tags list (optional)
            due_date: New due date in ISO 8601 format (optional)
            recurrence_rule: New recurrence rule (optional)
            reminder_offset: New reminder offset in hours (optional)
        """
        try:
            task = await self.db.run_sync(lambda s: crud_get_task(s, task_id, user_id))
            if not task:
                return {
                    "success": False,
                    "message": f"❌ Task {task_id} not found.",
                }

            # Validate priority if provided
            if priority and priority not in ["low", "medium", "high"]:
                return {
                    "success": False,
                    "message": f"❌ Invalid priority '{priority}'. Must be 'low', 'medium', or 'high'.",
                }

            # Validate tags if provided
            if tags is not None:
                if len(tags) > 20:
                    return {
                        "success": False,
                        "message": "❌ Maximum 20 tags allowed.",
                    }
                for tag in tags:
                    if not tag or len(tag) > 50:
                        return {
                            "success": False,
                            "message": "❌ Each tag must be 1-50 characters.",
                        }

            # Validate reminder_offset if provided
            if reminder_offset is not None:
                if reminder_offset < 0 or reminder_offset > 10080:
                    return {
                        "success": False,
                        "message": "❌ Reminder offset must be between 0 and 10080 hours (7 days).",
                    }

            # Parse due_date if provided
            from datetime import datetime
            parsed_due_date = None
            if due_date:
                try:
                    parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                except ValueError:
                    return {
                        "success": False,
                        "message": f"❌ Invalid due date format. Expected ISO 8601, got: {due_date}",
                    }

            task_update = TaskUpdate(
                title=title,
                description=description,
                completed=completed,
                priority=priority,
                tags=tags,
                due_date=parsed_due_date,
                recurrence_rule=recurrence_rule,
                reminder_offset=reminder_offset
            )
            updated_task = await self.db.run_sync(
                lambda s: crud_update_task(s, task_id, task_update, user_id)
            )
            if not updated_task:
                return {
                    "success": False,
                    "message": f"❌ Failed to update task {task_id}.",
                }

            # Check if recurring and completed (next instance auto-created)
            recurring_message = ""
            if completed and updated_task.recurrence_rule:
                recurring_message = f"\n🔁 Next instance of this recurring task has been created automatically."

            return {
                "success": True,
                "message": f"✏️ Task '{updated_task.title}' has been updated successfully.{recurring_message}",
                "task": {
                    "id": updated_task.id,
                    "title": updated_task.title,
                    "description": updated_task.description,
                    "completed": updated_task.completed,
                    "priority": updated_task.priority,
                    "tags": updated_task.tags,
                    "due_date": updated_task.due_date.isoformat() if updated_task.due_date else None,
                    "recurrence_rule": updated_task.recurrence_rule,
                    "reminder_offset": updated_task.reminder_offset,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error updating task: {str(e)}",
            }

    async def complete_task(self, user_id: int, task_id: int) -> dict:
        """Mark a task as complete (shorthand for update_task with completed=True).

        This helper automatically handles recurring task auto-creation.
        """
        return await self.update_task(user_id, task_id, completed=True)

    async def delete_task(self, user_id: int, task_id: int) -> dict:
        """Delete a task for the user."""
        try:
            task = await self.db.run_sync(lambda s: crud_get_task(s, task_id, user_id))
            if not task:
                return {
                    "success": False,
                    "message": f"❌ Task {task_id} not found.",
                }

            task_title = task.title
            success = await self.db.run_sync(lambda s: crud_delete_task(s, task_id, user_id))
            if not success:
                return {
                    "success": False,
                    "message": f"❌ Failed to delete task {task_id}.",
                }
            return {
                "success": True,
                "message": f"🗑️ Task '{task_title}' has been deleted successfully.",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error deleting task: {str(e)}",
            }
