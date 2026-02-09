export interface Task {
  id: number
  title: string
  description?: string
  completed: boolean
  createdAt: string
  updatedAt: string
  // Phase 5 Part A fields
  priority: 'low' | 'medium' | 'high'
  tags: string[]
  due_date?: string
  recurrence_rule?: string
  reminder_offset?: number
  is_overdue?: boolean
}

export interface TaskCreateInput {
  title: string
  description?: string
  // Phase 5 Part A fields
  priority?: 'low' | 'medium' | 'high'
  tags?: string[]
  due_date?: string
  recurrence_rule?: string
  reminder_offset?: number
}

export interface TaskUpdateInput extends Partial<TaskCreateInput> {
  completed?: boolean
}