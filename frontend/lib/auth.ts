import { createAuthClient } from 'better-auth/client'

// Initialize Better Auth client
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000',
})

// Export the useSession hook directly from better-auth/client
export { useSession } from 'better-auth/client'