'use client'

import { authClient } from '@/lib/auth'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function Header() {
  const router = useRouter()

  const handleSignOut = async () => {
    await authClient.signOut()
    router.push('/signin')
    router.refresh()
  }

  return (
    <header className="fixed top-0 left-0 right-0 bg-slate-900/60 backdrop-blur-md border-b border-slate-700/50 z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link href="/" className="text-xl font-bold text-cyan-400">
              AI Todo
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            <nav className="hidden md:block">
              <ul className="flex space-x-6">
                <li>
                  <Link
                    href="/"
                    className="text-slate-300 hover:text-cyan-400 transition-colors"
                  >
                    Home
                  </Link>
                </li>
                <li>
                  <Link
                    href="/tasks"
                    className="text-slate-300 hover:text-cyan-400 transition-colors"
                  >
                    Tasks
                  </Link>
                </li>
              </ul>
            </nav>
            <button
              onClick={handleSignOut}
              className="text-slate-300 hover:text-rose-500 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}