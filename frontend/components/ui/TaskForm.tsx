'use client'

import { useState } from 'react'
import { Task, TaskCreateInput, TaskUpdateInput } from '@/lib/types'
import GlassCard from './GlassCard'

interface TaskFormProps {
  task?: Task
  onSubmit: (taskData: TaskCreateInput | TaskUpdateInput) => void
  onCancel?: () => void
}

export default function TaskForm({ task, onSubmit, onCancel }: TaskFormProps) {
  const [title, setTitle] = useState(task?.title || '')
  const [description, setDescription] = useState(task?.description || '')
  const [completed, setCompleted] = useState(task?.completed || false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const taskData: TaskCreateInput | TaskUpdateInput = {
        title,
        description: description || undefined,
      }

      if (task) {
        // For updates, include completed status if it was provided
        (taskData as TaskUpdateInput).completed = completed
      }

      await onSubmit(taskData)
    } catch (error) {
      console.error('Error submitting task:', error)
      alert('Failed to save task')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <GlassCard>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-slate-300 mb-1">
            Title *
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white"
            placeholder="Task title"
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-slate-300 mb-1">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white"
            placeholder="Task description (optional)"
            disabled={isLoading}
          />
        </div>

        {task && (
          <div className="flex items-center">
            <input
              id="completed"
              type="checkbox"
              checked={completed}
              onChange={(e) => setCompleted(e.target.checked)}
              className="h-4 w-4 text-cyan-500 rounded focus:ring-cyan-400/60 border-slate-700 bg-slate-800"
              disabled={isLoading}
            />
            <label htmlFor="completed" className="ml-2 block text-sm text-slate-300">
              Completed
            </label>
          </div>
        )}

        <div className="flex space-x-3 pt-2">
          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 bg-gradient-to-r from-cyan-400 to-purple-500 hover:from-cyan-300 hover:to-purple-400 text-white py-2 px-4 rounded-lg transition-all duration-200 shadow-glow-lg disabled:opacity-50"
          >
            {isLoading ? 'Saving...' : task ? 'Update Task' : 'Create Task'}
          </button>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              disabled={isLoading}
              className="flex-1 bg-slate-700 text-slate-200 py-2 px-4 rounded-lg hover:bg-slate-600 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </GlassCard>
  )
}