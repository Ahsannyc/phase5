/**
 * Better Auth + JWT Configuration for Next.js
 * Sets up authentication client with JWT plugin
 */

import { createAuth } from "better-auth";
import { jwt } from "better-auth/plugins";

// Initialize Better Auth with JWT plugin
export const auth = createAuth({
  secret: process.env.BETTER_AUTH_SECRET || "fallback-secret-change-me",
  plugins: [
    jwt({
      secret: process.env.JWT_SECRET || "fallback-jwt-secret-change-me",
      expiresIn: "7d", // Token expires in 7 days
    }),
  ],
  // Add your providers here (Google, GitHub, etc.)
  socialProviders: {
    // google: {
    //   clientId: process.env.GOOGLE_CLIENT_ID || "",
    //   clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    // },
  },
});

// Type for the authenticated session
export type Session = Awaited<ReturnType<typeof auth.api.getSession>>;

// Export the client configuration for use in client components
export const authClient = auth.client;