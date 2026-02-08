'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api'
import TaskList from '@/components/ui/TaskList'
import EmptyState from '@/components/ui/EmptyState'
import FAB from '@/components/ui/FAB'
import LoadingSkeleton from '@/components/ui/LoadingSkeleton'
import { Task } from '@/lib/types'
import { useRouter } from 'next/navigation'

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    fetchTasks()
  }, [])

  const fetchTasks = async () => {
    try {
      setLoading(true)
      const tasksData = await apiClient.getTasks()
      setTasks(tasksData)
    } catch (error) {
      console.error('Error fetching tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTaskToggle = (updatedTask: Task) => {
    setTasks(tasks.map(task =>
      task.id === updatedTask.id ? updatedTask : task
    ))
  }

  const handleTaskDelete = (deletedTaskId: number) => {
    setTasks(tasks.filter(task => task.id !== deletedTaskId))
  }

  const handleCreateTask = () => {
    router.push('/tasks/new')
  }

  return (
    <div className="max-w-4xl mx-auto p-4 pb-24">
      <h1 className="text-3xl font-bold text-slate-100 mb-6">Your Tasks</h1>

      {loading ? (
        <LoadingSkeleton />
      ) : tasks.length === 0 ? (
        <EmptyState
          title="Initialize your task matrix"
          description="No tasks found. Create your first task to get started."
          actionText="Create Task"
          onAction={handleCreateTask}
        />
      ) : (
        <TaskList
          tasks={tasks}
          onToggleComplete={handleTaskToggle}
          onDelete={handleTaskDelete}
          onEdit={(task) => router.push(`/tasks/${task.id}/edit`)}
        />
      )}

      <FAB onClick={handleCreateTask} icon="+" label="Add Task" />
    </div>
  )
}