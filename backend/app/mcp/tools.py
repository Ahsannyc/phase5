"""MCP tools for task management."""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.task import Task, TaskCreate, TaskUpdate
from typing import Optional, Dict, Any


class TodoTools:
    """Tools for managing tasks through the MCP interface."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session."""
        self.db = db

    async def add_task(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a new task for a user."""
        try:
            task = Task(
                user_id=user_id,
                title=title,
                description=description or ""
            )
            self.db.add(task)
            await self.db.commit()
            await self.db.refresh(task)

            return {
                "message": f"✅ Task added: '{title}' (ID: {task.id})",
                "task_id": task.id,
                "success": True
            }
        except Exception as e:
            await self.db.rollback()
            return {
                "message": f"❌ Failed to add task: {str(e)}",
                "success": False
            }

    async def list_tasks(
        self,
        user_id: int,
        completed_only: bool = False
    ) -> Dict[str, Any]:
        """List tasks for a user."""
        try:
            stmt = select(Task).where(Task.user_id == user_id)
            if completed_only:
                stmt = stmt.where(Task.completed == True)
            stmt = stmt.order_by(Task.created_at.desc())

            result = await self.db.execute(stmt)
            tasks = result.scalars().all()

            if not tasks:
                status = "completed" if completed_only else "available"
                return {
                    "message": f"📋 No {status} tasks found.",
                    "tasks": [],
                    "count": 0
                }

            task_list = []
            for task in tasks:
                status = "✅" if task.completed else "⭕"
                task_list.append(
                    f"{status} [{task.id}] {task.title}"
                    + (f"\n    {task.description}" if task.description else "")
                )

            message = "📋 **Your Tasks:**\n" + "\n".join(task_list)
            return {
                "message": message,
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "description": t.description,
                        "completed": t.completed
                    }
                    for t in tasks
                ],
                "count": len(tasks)
            }
        except Exception as e:
            return {
                "message": f"❌ Failed to list tasks: {str(e)}",
                "tasks": [],
                "count": 0
            }

    async def complete_task(
        self,
        user_id: int,
        task_id: int
    ) -> Dict[str, Any]:
        """Mark a task as complete."""
        try:
            stmt = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            result = await self.db.execute(stmt)
            task = result.scalars().first()

            if not task:
                return {
                    "message": f"❌ Task {task_id} not found.",
                    "success": False
                }

            task.completed = True
            self.db.add(task)
            await self.db.commit()
            await self.db.refresh(task)

            return {
                "message": f"✅ Task '{task.title}' marked as complete!",
                "task_id": task.id,
                "success": True
            }
        except Exception as e:
            await self.db.rollback()
            return {
                "message": f"❌ Failed to complete task: {str(e)}",
                "success": False
            }

    async def delete_task(
        self,
        user_id: int,
        task_id: int
    ) -> Dict[str, Any]:
        """Delete a task."""
        try:
            stmt = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            result = await self.db.execute(stmt)
            task = result.scalars().first()

            if not task:
                return {
                    "message": f"❌ Task {task_id} not found.",
                    "success": False
                }

            task_title = task.title
            await self.db.delete(task)
            await self.db.commit()

            return {
                "message": f"🗑️ Task '{task_title}' deleted.",
                "task_id": task_id,
                "success": True
            }
        except Exception as e:
            await self.db.rollback()
            return {
                "message": f"❌ Failed to delete task: {str(e)}",
                "success": False
            }

    async def update_task(
        self,
        user_id: int,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a task."""
        try:
            stmt = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            result = await self.db.execute(stmt)
            task = result.scalars().first()

            if not task:
                return {
                    "message": f"❌ Task {task_id} not found.",
                    "success": False
                }

            if title:
                task.title = title
            if description is not None:
                task.description = description

            self.db.add(task)
            await self.db.commit()
            await self.db.refresh(task)

            return {
                "message": f"✏️ Task '{task.title}' updated.",
                "task_id": task.id,
                "success": True
            }
        except Exception as e:
            await self.db.rollback()
            return {
                "message": f"❌ Failed to update task: {str(e)}",
                "success": False
            }
