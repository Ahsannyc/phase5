'use client'

import { useState, useEffect } from 'react'

interface FABProps {
  onClick: () => void
  icon?: string
  label?: string
}

export default function FAB({ onClick, icon = '+', label = 'Add Task' }: FABProps) {
  const [isVisible, setIsVisible] = useState(true)
  const [isHovered, setIsHovered] = useState(false)

  // Simple animation effect
  useEffect(() => {
    let timeoutId: NodeJS.Timeout

    if (isHovered) {
      timeoutId = setTimeout(() => {
        setIsHovered(false)
      }, 1000) // Reset hover effect after 1 second
    }

    return () => {
      if (timeoutId) clearTimeout(timeoutId)
    }
  }, [isHovered])

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      className={`
        fixed bottom-8 right-8 z-50
        w-14 h-14 rounded-full
        bg-gradient-to-r from-cyan-400 to-purple-500
        hover:from-cyan-300 hover:to-purple-400
        text-white text-2xl
        flex items-center justify-center
        shadow-glow-lg hover:shadow-cyan-400/50
        transform transition-all duration-300
        hover:scale-110
        ${isHovered ? 'animate-pulse' : ''}
        focus:outline-none focus:ring-2 focus:ring-cyan-400/60
      `}
      aria-label={label}
    >
      {icon}
    </button>
  )
}