import TaskCard from './TaskCard'
import { Task } from '@/lib/types'

interface TaskListProps {
  tasks: Task[]
  onToggleComplete?: (task: Task) => void
  onEdit?: (task: Task) => void
  onDelete?: (taskId: number) => void
}

export default function TaskList({
  tasks,
  onToggleComplete,
  onEdit,
  onDelete
}: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <div className="text-center py-12 text-slate-400">
        <p className="text-lg">No tasks found</p>
        <p className="text-sm mt-1">Create your first task to get started</p>
      </div>
    )
  }

  return (
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
  )
}