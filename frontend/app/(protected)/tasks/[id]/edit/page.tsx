'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { apiClient } from '@/lib/api'
import TaskForm from '@/components/ui/TaskForm'
import { Task } from '@/lib/types'

export default function EditTaskPage() {
  const router = useRouter()
  const params = useParams()
  const taskId = parseInt(Array.isArray(params.id) ? params.id[0] : params.id)

  const [task, setTask] = useState<Task | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTask()
  }, [])

  const fetchTask = async () => {
    try {
      setLoading(true)
      const taskData = await apiClient.getTaskById(taskId)
      setTask(taskData)
    } catch (error) {
      console.error('Error fetching task:', error)
      router.push('/') // Redirect if task not found
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (taskData: Partial<Task>) => {
    try {
      await apiClient.updateTask(taskId, taskData as any) // Type assertion for partial update
      router.push('/') // Redirect to dashboard after updating
      router.refresh()
    } catch (error) {
      console.error('Error updating task:', error)
      alert('Failed to update task')
    }
  }

  const handleCancel = () => {
    router.back()
  }

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-cyan-400 mx-auto mt-10"></div>
      </div>
    )
  }

  if (!task) {
    return (
      <div className="max-w-2xl mx-auto p-4 text-center">
        <p className="text-slate-400">Task not found</p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold text-slate-100 mb-6">Edit Task</h1>
      <TaskForm task={task} onSubmit={handleSubmit} onCancel={handleCancel} />
    </div>
  )
}