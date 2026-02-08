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

    async def add_task(self, user_id: int, title: str, description: str = None) -> dict:
        """Add a new task for the user."""
        try:
            task_create = TaskCreate(title=title, description=description)
            task = await self.db.run_sync(lambda s: crud_create_task(s, task_create, user_id))
            return {
                "success": True,
                "message": f"✅ Task '{title}' has been created successfully.",
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error creating task: {str(e)}",
            }

    async def list_tasks(self, user_id: int, completed_only: bool = False) -> dict:
        """List all tasks for the user."""
        try:
            tasks = await self.db.run_sync(lambda s: crud_get_tasks(s, user_id))
            if completed_only:
                tasks = [t for t in tasks if t.completed]

            if not tasks:
                return {
                    "success": True,
                    "message": "📋 You have no tasks yet. Create one with 'add task [name]'!",
                    "tasks": [],
                }

            task_list = "\n".join([
                f"{'✅' if t.completed else '⭕'} Task {t.id}: {t.title}" +
                (f" - {t.description}" if t.description else "")
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
                    }
                    for t in tasks
                ],
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error listing tasks: {str(e)}",
            }

    async def update_task(self, user_id: int, task_id: int, title: str = None, description: str = None) -> dict:
        """Update a task for the user."""
        try:
            task = await self.db.run_sync(lambda s: crud_get_task(s, task_id, user_id))
            if not task:
                return {
                    "success": False,
                    "message": f"❌ Task {task_id} not found.",
                }

            task_update = TaskUpdate(title=title, description=description)
            updated_task = await self.db.run_sync(
                lambda s: crud_update_task(s, task_id, task_update, user_id)
            )
            if not updated_task:
                return {
                    "success": False,
                    "message": f"❌ Failed to update task {task_id}.",
                }
            return {
                "success": True,
                "message": f"✏️ Task '{updated_task.title}' has been updated successfully.",
                "task": {
                    "id": updated_task.id,
                    "title": updated_task.title,
                    "description": updated_task.description,
                    "completed": updated_task.completed,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error updating task: {str(e)}",
            }

    async def complete_task(self, user_id: int, task_id: int) -> dict:
        """Mark a task as complete."""
        try:
            updated_task = await self.db.run_sync(
                lambda s: crud_toggle_task(s, task_id, True, user_id)
            )
            if not updated_task:
                return {
                    "success": False,
                    "message": f"❌ Task {task_id} not found.",
                }
            return {
                "success": True,
                "message": f"✅ Task '{updated_task.title}' has been marked as complete!",
                "task": {
                    "id": updated_task.id,
                    "title": updated_task.title,
                    "description": updated_task.description,
                    "completed": updated_task.completed,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error completing task: {str(e)}",
            }

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
