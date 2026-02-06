import { Task, TaskCreateInput, TaskUpdateInput } from './types'

interface ApiResponse<T> {
  data?: T
  error?: string
  isLoading: boolean
}

class ApiClient {
  private baseUrl: string

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      const errorData = await response.text()
      throw new Error(errorData || `HTTP error! status: ${response.status}`)
    }

    return response.json() as Promise<T>
  }

  async getTasks(): Promise<Task[]> {
    try {
      return await this.request<Task[]>('/api/tasks')
    } catch (error) {
      console.error('Error fetching tasks:', error)
      throw error
    }
  }

  async createTask(taskData: TaskCreateInput): Promise<Task> {
    try {
      return await this.request<Task>('/api/tasks', {
        method: 'POST',
        body: JSON.stringify(taskData),
      })
    } catch (error) {
      console.error('Error creating task:', error)
      throw error
    }
  }

  async updateTask(id: number, taskData: TaskUpdateInput): Promise<Task> {
    try {
      return await this.request<Task>(`/api/tasks/${id}`, {
        method: 'PUT',
        body: JSON.stringify(taskData),
      })
    } catch (error) {
      console.error('Error updating task:', error)
      throw error
    }
  }

  async deleteTask(id: number): Promise<void> {
    try {
      await this.request(`/api/tasks/${id}`, {
        method: 'DELETE',
      })
    } catch (error) {
      console.error('Error deleting task:', error)
      throw error
    }
  }

  async getTaskById(id: number): Promise<Task> {
    try {
      return await this.request<Task>(`/api/tasks/${id}`)
    } catch (error) {
      console.error('Error fetching task:', error)
      throw error
    }
  }

  async toggleComplete(id: number, completed: boolean): Promise<Task> {
    try {
      return await this.request<Task>(`/api/tasks/${id}/complete`, {
        method: 'PATCH',
        body: JSON.stringify({ completed }),
      })
    } catch (error) {
      console.error('Error toggling task completion:', error)
      throw error
    }
  }
}

export const apiClient = new ApiClient()