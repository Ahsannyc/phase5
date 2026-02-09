'use client'

import TaskCard from './TaskCard'
import TaskListControls, { TaskFilters } from './TaskListControls'
import { Task } from '@/lib/types'
import { useState, useEffect } from 'react'

interface TaskListProps {
  tasks: Task[]
  onToggleComplete?: (task: Task) => void
  onEdit?: (task: Task) => void
  onDelete?: (taskId: number) => void
  onFilterChange?: (filters: TaskFilters) => void
}

export default function TaskList({
  tasks,
  onToggleComplete,
  onEdit,
  onDelete,
  onFilterChange
}: TaskListProps) {
  const [filters, setFilters] = useState<TaskFilters>({
    search: '',
    priority: '',
    tags: [],
    status: '',
    sort: 'created_at'
  })

  const handleFilterChange = (newFilters: TaskFilters) => {
    setFilters(newFilters)
    onFilterChange?.(newFilters)
  }

  if (tasks.length === 0) {
    return (
      <>
        <TaskListControls onFilterChange={handleFilterChange} />
        <div className="text-center py-12 text-slate-400">
          <p className="text-lg">No tasks found</p>
          <p className="text-sm mt-1">Try adjusting your filters or create a new task</p>
        </div>
      </>
    )
  }

  return (
    <>
      <TaskListControls onFilterChange={handleFilterChange} />
      <div className="space-y-4">
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onToggleComplete={onToggleComplete}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        ))}
      </div>
    </>
  )
}