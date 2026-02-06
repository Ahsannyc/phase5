import { NextRequest, NextResponse } from 'next/server'

export function middleware(request: NextRequest) {
  // Add any global middleware logic here if needed
  // Currently just pass through
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'], // Run middleware on all routes except static files
}