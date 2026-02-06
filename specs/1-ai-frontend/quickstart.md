# Quickstart Guide: AI-Themed Todo Frontend

## Overview
This guide provides step-by-step instructions to set up, develop, and deploy the AI-themed Todo frontend application. Follow these instructions to get the application running locally and understand the development workflow.

## Prerequisites

Before starting, ensure you have the following installed:

- Node.js (version 18.x or higher)
- npm (version 8.x or higher) or yarn
- Git
- A code editor (VS Code recommended)

## Initial Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd todo-phase2/frontend
```

### 2. Install Dependencies
```bash
npm install
# or
yarn install
```

### 3. Environment Configuration
Create a `.env.local` file in the frontend directory with the following variables:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
BETTER_AUTH_URL=http://localhost:3000
```

## Development

### 1. Running the Development Server
```bash
npm run dev
# or
yarn dev
```

The application will start at `http://localhost:3000`

### 2. Development Commands

- `npm run dev` - Start development server with hot reloading
- `npm run build` - Build the application for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint to check for code issues
- `npm run type-check` - Run TypeScript compiler in check mode
- `npm run test` - Run unit tests (if configured)
- `npm run test:watch` - Run unit tests in watch mode (if configured)

### 3. Folder Structure for Development

Understanding the key folders and files:

```
frontend/
├── app/
│   ├── (auth)/          # Authentication-related pages
│   │   ├── signin/
│   │   └── signup/
│   ├── (protected)/     # Protected routes for logged-in users
│   │   ├── layout.tsx
│   │   ├── page.tsx     # Dashboard/home page
│   │   └── tasks/
│   │       ├── new/
│   │       └── [id]/
│   │           └── edit/
│   ├── layout.tsx       # Root layout
│   └── page.tsx         # Landing page
├── components/          # Reusable UI components
│   ├── ui/
│   ├── layout/
│   └── auth/
├── lib/                # Utility functions and API clients
│   ├── api.ts          # Centralized API client
│   ├── auth.ts         # Authentication helpers
│   └── types.ts        # Shared TypeScript types
├── hooks/              # Custom React hooks
├── styles/             # Styling configuration
│   └── tailwind.config.ts
└── public/             # Static assets
```

## Key Development Concepts

### 1. Component Strategy
- **Server Components**: Default for static content, better performance
- **Client Components**: Only when interactivity is needed (use 'use client')
- **Shared Components**: Reusable UI elements in the `components/` directory

### 2. Styling with Tailwind
- Use Tailwind utility classes exclusively
- Custom AI-themed extensions defined in `tailwind.config.ts`
- Common classes for glassmorphism: `bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 shadow-glow`
- Common classes for neon effects: `shadow-[0_0_20px_#22d3ee33] ring-cyan-400/40`

### 3. Authentication Flow
- Better Auth integration for user management
- Protected routes using the `(protected)` route group
- Automatic token handling in API client
- Redirect logic for unauthorized access

### 4. API Integration
- Centralized API client in `lib/api.ts`
- Automatic JWT token attachment
- Error handling and user feedback
- Type-safe API calls

## Building for Production

### 1. Create Production Build
```bash
npm run build
```

### 2. Run Production Server
```bash
npm run start
```

## Environment Variables

Required environment variables for different environments:

### Development
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
BETTER_AUTH_URL=http://localhost:3000
```

### Production
```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.com
NEXTAUTH_URL=https://your-frontend-domain.com
BETTER_AUTH_URL=https://your-frontend-domain.com
```

## Troubleshooting

### Common Issues

1. **Module not found errors**
   - Run `npm install` to ensure all dependencies are installed
   - Check if you're in the correct directory (frontend/)

2. **Tailwind classes not working**
   - Verify that `tailwind.config.ts` is properly configured
   - Ensure `globals.css` imports Tailwind directives
   - Restart dev server after config changes

3. **Authentication not working**
   - Check environment variables are set correctly
   - Verify backend API is running and accessible
   - Ensure JWT secret matches between frontend and backend

4. **API calls failing**
   - Verify NEXT_PUBLIC_API_BASE_URL is set correctly
   - Check that backend is running and accessible
   - Look for CORS errors in browser console

### Development Tips

- Use the VS Code extension for Tailwind CSS IntelliSense
- Enable TypeScript checking during development to catch type errors early
- Use React Developer Tools browser extension for debugging components
- Check browser console for detailed error messages

## Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on pushes to main branch

### Other Platforms
- Ensure Node.js environment is available
- Set environment variables appropriately
- Pre-build step should run `npm run build`

## Next Steps

After completing the setup:

1. Explore the existing components in `components/ui/`
2. Review the API client in `lib/api.ts` to understand API integration
3. Check the authentication flow in the `(auth)` and `(protected)` route groups
4. Familiarize yourself with the AI-themed design system in `styles/tailwind.config.ts`
5. Run the development server and explore the current functionality