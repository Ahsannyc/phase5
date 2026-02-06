"""Tasks API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_async_session
from app.schemas.task import TaskCreate, TaskUpdate, TaskToggle, TaskResponse
from app.models.task import Task
from app.crud.task import (
    create_task as crud_create_task,
    get_tasks_by_user as crud_get_tasks_by_user,
    get_task_by_id_and_user as crud_get_task_by_id_and_user,
    update_task as crud_update_task,
    delete_task as crud_delete_task,
    toggle_task_completion as crud_toggle_task_completion
)
from app.api.deps import get_current_user
from typing import List, Any


tasks_router = APIRouter()


@tasks_router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    current_user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """List all tasks for the current user."""
    tasks = await db.run_sync(lambda session: crud_get_tasks_by_user(session, current_user_id))
    return tasks


@tasks_router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task_create: TaskCreate,
    current_user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Create a new task for the current user."""
    db_task = await db.run_sync(
        lambda session: crud_create_task(session, task_create, current_user_id)
    )
    return db_task


@tasks_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Get a specific task by ID for the current user."""
    task = await db.run_sync(
        lambda session: crud_get_task_by_id_and_user(session, task_id, current_user_id)
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to access it"
        )
    return task


@tasks_router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Update a specific task for the current user."""
    updated_task = await db.run_sync(
        lambda session: crud_update_task(session, task_id, task_update, current_user_id)
    )
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to update it"
        )
    return updated_task


@tasks_router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: int,
    task_toggle: TaskToggle,
    current_user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Toggle the completion status of a specific task."""
    updated_task = await db.run_sync(
        lambda session: crud_toggle_task_completion(session, task_id, task_toggle.completed, current_user_id)
    )
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to update it"
        )
    return updated_task


@tasks_router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    current_user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Delete a specific task for the current user."""
    success = await db.run_sync(
        lambda session: crud_delete_task(session, task_id, current_user_id)
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to delete it"
        )
    return None  # Returning None for 204 status code