import GlassCard from './GlassCard'

interface EmptyStateProps {
  title?: string
  description?: string
  actionText?: string
  onAction?: () => void
}

export default function EmptyState({
  title = "Initialize your task matrix",
  description = "No tasks found. Create your first task to get started.",
  actionText = "Create Task",
  onAction
}: EmptyStateProps) {
  return (
    <GlassCard className="text-center py-12">
      <div className="mx-auto h-16 w-16 flex items-center justify-center rounded-full bg-slate-800 mb-4">
        <span className="text-2xl">📋</span>
      </div>
      <h3 className="text-xl font-medium text-slate-100 mb-2">{title}</h3>
      <p className="text-slate-400 mb-6">{description}</p>
      {onAction && (
        <button
          onClick={onAction}
          className="bg-gradient-to-r from-cyan-400 to-purple-500 hover:from-cyan-300 hover:to-purple-400 text-white py-2 px-6 rounded-lg transition-all duration-200 shadow-glow-lg"
        >
          {actionText}
        </button>
      )}
    </GlassCard>
  )
}