import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-slate-100 mb-2">AI-Themed Todo</h1>
          <p className="text-slate-400">A futuristic task management experience</p>
        </div>
        <div className="mt-8 bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-xl p-8 shadow-glow">
          <div className="space-y-4">
            <Link
              href="/signin"
              className="w-full bg-gradient-to-r from-cyan-400 to-purple-500 hover:from-cyan-300 hover:to-purple-400 text-white py-3 px-4 rounded-lg transition-all duration-200 shadow-glow-lg block text-center"
            >
              Sign In
            </Link>
            <Link
              href="/signup"
              className="w-full bg-slate-800 text-slate-100 py-3 px-4 rounded-lg border border-slate-700 block text-center"
            >
              Sign Up
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}