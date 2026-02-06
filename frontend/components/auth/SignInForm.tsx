'use client'

import { useState } from 'react'
import { authClient } from '@/lib/auth'
import { useRouter } from 'next/navigation'
import GlassCard from '@/components/ui/GlassCard'

export default function SignInForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const response = await authClient.signIn.email({
        email,
        password,
      })

      if (!response) {
        router.push('/tasks')
        router.refresh()
      } else {
        setError('Invalid email or password')
      }
    } catch (err) {
      setError('An unexpected error occurred')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <GlassCard>
      <h2 className="text-2xl font-bold text-slate-100 mb-6 text-center">Sign In</h2>
      {error && (
        <div className="mb-4 p-3 bg-rose-900/50 text-rose-200 rounded-lg text-sm">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-1">
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white"
            placeholder="your@email.com"
            disabled={isLoading}
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-1">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full px-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:border-cyan-400/60 text-white"
            placeholder="••••••••"
            disabled={isLoading}
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-cyan-400 to-purple-500 hover:from-cyan-300 hover:to-purple-400 text-white py-3 px-4 rounded-lg transition-all duration-200 shadow-glow-lg disabled:opacity-50"
        >
          {isLoading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>
      <div className="mt-4 text-center text-sm text-slate-400">
        Don't have an account?{' '}
        <a href="/signup" className="text-cyan-400 hover:text-cyan-300 underline">
          Sign up
        </a>
      </div>
    </GlassCard>
  )
}