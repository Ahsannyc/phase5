'use client'

import { useState, useEffect } from 'react'

interface AnimatedCheckboxProps {
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
}

export default function AnimatedCheckbox({
  checked,
  onChange,
  disabled = false
}: AnimatedCheckboxProps) {
  const [isChecked, setIsChecked] = useState(checked)
  const [isAnimating, setIsAnimating] = useState(false)

  useEffect(() => {
    setIsChecked(checked)
  }, [checked])

  const handleClick = () => {
    if (disabled) return

    const newValue = !isChecked
    setIsChecked(newValue)
    setIsAnimating(true)

    setTimeout(() => {
      onChange(newValue)
      setIsAnimating(false)
    }, 300) // Match animation duration
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled}
      className={`
        relative h-6 w-6 rounded-md border-2 flex items-center justify-center
        transition-all duration-200 ease-in-out transform
        ${isAnimating ? 'scale-110' : 'scale-100'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${isChecked
          ? 'bg-gradient-to-r from-cyan-400 to-purple-500 border-transparent'
          : 'border-slate-500 hover:border-cyan-400 hover:shadow-glow'
        }
        ${isAnimating && isChecked ? 'shadow-glow-lg shadow-cyan-400/50' : ''}
      `}
      aria-checked={isChecked}
      role="checkbox"
      aria-label="Toggle task completion"
    >
      {isChecked && (
        <svg
          className="h-4 w-4 text-white"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="20,6 9,17 4,12" />
        </svg>
      )}
      {isAnimating && isChecked && (
        <span
          className={`
            absolute inset-0 rounded-md border-2 border-cyan-400
            animate-ping opacity-75
          `}
        />
      )}
    </button>
  )
}