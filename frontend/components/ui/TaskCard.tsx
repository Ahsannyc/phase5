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

  const getPriorityStyles = () => {
    switch (task.priority) {
      case 'high':
        return 'bg-red-500/20 text-red-300 border-red-500/50'
      case 'medium':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50'
      case 'low':
        return 'bg-green-500/20 text-green-300 border-green-500/50'
      default:
        return 'bg-gray-500/20 text-gray-300 border-gray-500/50'
    }
  }

  return (
    <div className={`bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6 shadow-glow transition-all duration-200 hover:shadow-cyan-500/20 hover:border-cyan-400/40 ${
      task.completed ? 'border-purple-500/40' : ''
    } ${task.is_overdue ? 'border-red-500/60' : ''}`}>
      <div className="flex items-start space-x-4">
        <div className="pt-1">
          <AnimatedCheckbox
            checked={task.completed}
            onChange={handleToggleComplete}
            disabled={isDeleting}
          />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <h3 className={`text-lg font-medium ${
              task.completed ? 'text-slate-400 line-through' : 'text-slate-100'
            }`}>
              {task.title}
            </h3>
            <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getPriorityStyles()}`}>
              {task.priority.toUpperCase()}
            </span>
            {task.is_overdue && (
              <span className="px-2 py-0.5 rounded text-xs font-bold bg-red-600/30 text-red-200 border border-red-500/50">
                ⚠️ OVERDUE
              </span>
            )}
          </div>
          {task.description && (
            <p className={`mt-1 text-slate-300 ${
              task.completed ? 'text-slate-500' : ''
            }`}>
              {task.description}
            </p>
          )}
          {task.tags && task.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {task.tags.map(tag => (
                <span key={tag} className="bg-purple-500/20 text-purple-200 px-2 py-0.5 rounded text-xs border border-purple-500/40">
                  {tag}
                </span>
              ))}
            </div>
          )}
          {task.due_date && (
            <div className={`mt-2 text-sm ${task.is_overdue ? 'text-red-400 font-bold' : 'text-slate-400'}`}>
              📅 Due: {new Date(task.due_date).toLocaleString()}
            </div>
          )}
          {task.recurrence_rule && (
            <div className="mt-1 text-sm text-blue-400">
              🔄 Recurs: {task.recurrence_rule}
            </div>
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