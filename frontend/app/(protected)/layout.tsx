'use client'

import { authClient, useSession } from '@/lib/auth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Header from '@/components/layout/Header'
import { ChatInterface } from '@/components/chat/ChatInterface'

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/signin')
    }
  }, [status, router])

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-cyan-400"></div>
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return null // Redirect happens in useEffect
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <Header />
      <main className="pt-16">
        {children}
      </main>
      <ChatInterface />
    </div>
  )
}