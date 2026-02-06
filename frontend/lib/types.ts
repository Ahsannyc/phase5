export interface Task {
  id: number
  title: string
  description?: string
  completed: boolean
  createdAt: string
  updatedAt: string
}

export interface TaskCreateInput {
  title: string
  description?: string
}

export interface TaskUpdateInput extends Partial<TaskCreateInput> {
  completed?: boolean
}