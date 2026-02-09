'use client'

import { useState } from 'react'

export interface TaskFilters {
  search: string
  priority: string
  tags: string[]
  status: string
  sort: string
}

interface TaskListControlsProps {
  onFilterChange: (filters: TaskFilters) => void
}

export default function TaskListControls({ onFilterChange }: TaskListControlsProps) {
  const [filters, setFilters] = useState<TaskFilters>({
    search: '',
    priority: '',
    tags: [],
    status: '',
    sort: 'created_at'
  })

  const handleChange = (newFilters: Partial<TaskFilters>) => {
    const updated = { ...filters, ...newFilters }
    setFilters(updated)
    onFilterChange(updated)
  }

  const handleClear = () => {
    const cleared = {
      search: '',
      priority: '',
      tags: [],
      status: '',
      sort: 'created_at'
    }
    setFilters(cleared)
    onFilterChange(cleared)
  }

  return (
    <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-xl p-4 shadow-glow mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Search */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">
            Search
          </label>
          <input
            type="text"
            placeholder="Search tasks..."
            value={filters.search}
            onChange={(e) => handleChange({ search: e.target.value })}
            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white text-sm"
          />
        </div>

        {/* Priority filter */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">
            Priority
          </label>
          <select
            value={filters.priority}
            onChange={(e) => handleChange({ priority: e.target.value })}
            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white text-sm"
          >
            <option value="">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        {/* Status filter */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">
            Status
          </label>
          <select
            value={filters.status}
            onChange={(e) => handleChange({ status: e.target.value })}
            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white text-sm"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
          </select>
        </div>

        {/* Sort */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">
            Sort By
          </label>
          <select
            value={filters.sort}
            onChange={(e) => handleChange({ sort: e.target.value })}
            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white text-sm"
          >
            <option value="created_at">Newest First</option>
            <option value="-created_at">Oldest First</option>
            <option value="due_date">Due Date (Earliest)</option>
            <option value="-due_date">Due Date (Latest)</option>
            <option value="-priority">Priority (High First)</option>
            <option value="priority">Priority (Low First)</option>
            <option value="title">Title (A-Z)</option>
            <option value="-title">Title (Z-A)</option>
          </select>
        </div>
      </div>

      {/* Clear button */}
      <div className="mt-4 flex justify-end">
        <button
          onClick={handleClear}
          className="px-4 py-2 bg-slate-700 text-slate-200 rounded-lg hover:bg-slate-600 transition-colors text-sm"
        >
          Clear Filters
        </button>
      </div>
    </div>
  )
}
