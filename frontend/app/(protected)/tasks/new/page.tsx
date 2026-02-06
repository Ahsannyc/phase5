'use client'

import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import TaskForm from '@/components/ui/TaskForm'
import { TaskCreateInput } from '@/lib/types'

export default function NewTaskPage() {
  const router = useRouter()

  const handleSubmit = async (taskData: TaskCreateInput) => {
    try {
      await apiClient.createTask(taskData)
      router.push('/') // Redirect to dashboard after creating task
      router.refresh()
    } catch (error) {
      console.error('Error creating task:', error)
      alert('Failed to create task')
    }
  }

  const handleCancel = () => {
    router.back()
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold text-slate-100 mb-6">Create New Task</h1>
      <TaskForm onSubmit={handleSubmit} onCancel={handleCancel} />
    </div>
  )
}