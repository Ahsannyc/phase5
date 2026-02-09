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
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>(task?.priority || 'medium')
  const [tags, setTags] = useState<string[]>(task?.tags || [])
  const [tagInput, setTagInput] = useState('')
  const [dueDate, setDueDate] = useState(task?.due_date ? task.due_date.slice(0, 16) : '')
  const [recurrenceRule, setRecurrenceRule] = useState(task?.recurrence_rule || '')
  const [reminderOffset, setReminderOffset] = useState(task?.reminder_offset?.toString() || '')
  const [isLoading, setIsLoading] = useState(false)

  const handleAddTag = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault()
      if (!tags.includes(tagInput.trim()) && tags.length < 20) {
        setTags([...tags, tagInput.trim()])
        setTagInput('')
      }
    }
  }

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(t => t !== tagToRemove))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const taskData: TaskCreateInput | TaskUpdateInput = {
        title,
        description: description || undefined,
        priority,
        tags,
        due_date: dueDate || undefined,
        recurrence_rule: recurrenceRule || undefined,
        reminder_offset: reminderOffset ? parseInt(reminderOffset) : undefined,
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

        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-slate-300 mb-1">
            Priority
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as 'low' | 'medium' | 'high')}
            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white"
            disabled={isLoading}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div>
          <label htmlFor="tags" className="block text-sm font-medium text-slate-300 mb-1">
            Tags
          </label>
          <div className="flex flex-wrap gap-2 mb-2">
            {tags.map(tag => (
              <span key={tag} className="bg-purple-500/30 text-purple-200 px-2 py-1 rounded-lg text-sm flex items-center gap-1 border border-purple-500/50">
                {tag}
                <button
                  type="button"
                  onClick={() => removeTag(tag)}
                  className="text-purple-200 hover:text-white"
                  disabled={isLoading}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          <input
            id="tags"
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={handleAddTag}
            placeholder="Type and press Enter to add tag..."
            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white"
            disabled={isLoading || tags.length >= 20}
          />
          <p className="text-xs text-slate-400 mt-1">{tags.length}/20 tags</p>
        </div>

        <div>
          <label htmlFor="due_date" className="block text-sm font-medium text-slate-300 mb-1">
            Due Date
          </label>
          <input
            id="due_date"
            type="datetime-local"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white"
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="recurrence_rule" className="block text-sm font-medium text-slate-300 mb-1">
            Recurrence
          </label>
          <select
            id="recurrence_rule"
            value={recurrenceRule}
            onChange={(e) => setRecurrenceRule(e.target.value)}
            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white"
            disabled={isLoading}
          >
            <option value="">None</option>
            <option value="daily">Daily</option>
            <option value="weekly:monday">Weekly - Monday</option>
            <option value="weekly:tuesday">Weekly - Tuesday</option>
            <option value="weekly:wednesday">Weekly - Wednesday</option>
            <option value="weekly:thursday">Weekly - Thursday</option>
            <option value="weekly:friday">Weekly - Friday</option>
            <option value="weekly:saturday">Weekly - Saturday</option>
            <option value="weekly:sunday">Weekly - Sunday</option>
            <option value="monthly:1">Monthly - 1st</option>
            <option value="monthly:15">Monthly - 15th</option>
            <option value="monthly:last">Monthly - Last Day</option>
            <option value="yearly:january-1">Yearly - January 1st</option>
            <option value="yearly:march-15">Yearly - March 15th</option>
            <option value="yearly:december-25">Yearly - December 25th</option>
          </select>
        </div>

        <div>
          <label htmlFor="reminder_offset" className="block text-sm font-medium text-slate-300 mb-1">
            Reminder (hours before due date)
          </label>
          <input
            id="reminder_offset"
            type="number"
            value={reminderOffset}
            onChange={(e) => setReminderOffset(e.target.value)}
            min="0"
            max="10080"
            placeholder="0-10080 hours (max 7 days)"
            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white"
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