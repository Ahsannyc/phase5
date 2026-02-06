'use client'

import { Task } from '@/lib/types'
import { apiClient } from '@/lib/api'
import { useState } from 'react'
import AnimatedCheckbox from './AnimatedCheckbox'

interface TaskCardProps {
  task: Task
  onToggleComplete?: (task: Task) => void
  onEdit?: (task: Task) => void
  onDelete?: (taskId: number) => void
}

export default function TaskCard({
  task,
  onToggleComplete,
  onEdit,
  onDelete
}: TaskCardProps) {
  const [isDeleting, setIsDeleting] = useState(false)

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      setIsDeleting(true)
      try {
        await apiClient.deleteTask(task.id)
        onDelete?.(task.id)
      } catch (error) {
        console.error('Error deleting task:', error)
        alert('Failed to delete task')
      } finally {
        setIsDeleting(false)
      }
    }
  }

  const handleToggleComplete = async () => {
    try {
      const updatedTask = await apiClient.toggleComplete(task.id, !task.completed)
      onToggleComplete?.(updatedTask)
    } catch (error) {
      console.error('Error toggling task completion:', error)
      alert('Failed to update task completion')
    }
  }

  return (
    <div className={`bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6 shadow-glow transition-all duration-200 hover:shadow-cyan-500/20 hover:border-cyan-400/40 ${
      task.completed ? 'border-purple-500/40' : ''
    }`}>
      <div className="flex items-start space-x-4">
        <div className="pt-1">
          <AnimatedCheckbox
            checked={task.completed}
            onChange={handleToggleComplete}
            disabled={isDeleting}
          />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className={`text-lg font-medium ${
            task.completed ? 'text-slate-400 line-through' : 'text-slate-100'
          }`}>
            {task.title}
          </h3>
          {task.description && (
            <p className={`mt-1 text-slate-300 ${
              task.completed ? 'text-slate-500' : ''
            }`}>
              {task.description}
            </p>
          )}
          <div className="mt-2 text-xs text-slate-500">
            Updated: {new Date(task.updatedAt).toLocaleString()}
          </div>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => onEdit?.(task)}
            disabled={isDeleting}
            className="text-cyan-400 hover:text-cyan-300 p-1 disabled:opacity-50"
            aria-label="Edit task"
          >
            ✏️
          </button>
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="text-rose-500 hover:text-rose-400 p-1 disabled:opacity-50"
            aria-label="Delete task"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>
  )
}