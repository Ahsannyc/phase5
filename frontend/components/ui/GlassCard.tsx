import React from 'react'

interface GlassCardProps {
  children: React.ReactNode
  className?: string
}

export default function GlassCard({ children, className = '' }: GlassCardProps) {
  return (
    <div
      className={`bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6 shadow-glow ${className}`}
    >
      {children}
    </div>
  )
}