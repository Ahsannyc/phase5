export default function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      {[...Array(3)].map((_, index) => (
        <div
          key={index}
          className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6 shadow-glow animate-pulse"
        >
          <div className="flex items-center space-x-4">
            <div className="h-6 w-6 rounded-md bg-slate-700"></div>
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-slate-700 rounded w-3/4"></div>
              <div className="h-3 bg-slate-700 rounded w-1/2"></div>
              <div className="h-3 bg-slate-700 rounded w-2/3"></div>
            </div>
            <div className="h-6 w-12 bg-slate-700 rounded"></div>
          </div>
        </div>
      ))}
    </div>
  )
}