# Phase 2 – Todo Web Application
Frontend Specification v1.0 – AI-Themed Modern UI
Frontend-Only – Next.js App Router Focus

Date: December 2025
Version: v1.0
Status: Ready for immediate implementation by Frontend Engineer agent

## 1. Overview & Purpose

Build a **visually stunning, modern AI-themed frontend** for a multi-user Todo application using **Next.js 16+ (App Router)**, **TypeScript**, **Tailwind CSS**, and **Better Auth (with JWT plugin)**.

The UI should feel like a **next-generation AI-native dashboard** — futuristic, intelligent, sleek, with subtle cyber-tech aesthetics, glowing accents, glass-like surfaces, and a premium, high-tech atmosphere that reflects the "Cloud Native AI" and "Architecture of Intelligence" theme of the hackathon.

This specification covers **only the frontend layer**:
- AI-themed authentication UI and flow
- Protected AI-style dashboard and task management
- The **5 core Todo features**
- Centralized, typed API client with automatic JWT handling
- Delightful, smooth, and futuristic micro-interactions

No backend implementation, no database logic, no deployment configuration, and no advanced features are included.

Expected REST API contract (to be implemented later):

- POST   /api/auth/signup
- POST   /api/auth/signin
- GET    /api/tasks
- POST   /api/tasks
- GET    /api/tasks/:id
- PUT    /api/tasks/:id
- DELETE /api/tasks/:id
- PATCH  /api/tasks/:id/complete

All task endpoints require Authorization: Bearer <token>

## 2. The 5 Core Todo Features (must be fully implemented)

1. **Add / Create task**
   Create new task (title required, description optional)

2. **View / List tasks**
   Display only current user's tasks (beautiful empty state when none)

3. **Update / Edit task**
   Modify title and/or description of existing task

4. **Delete task**
   Remove task after confirmation

5. **Mark Complete / Toggle completion**
   Toggle task between completed ↔ pending (with satisfying animation)

All features must enforce user isolation, show loading/success/error states, and feel responsive and futuristic.

## 3. Core Requirements & Constraints

- Next.js 16+ App Router
- TypeScript strict mode
- Tailwind CSS utility classes **only** — no custom CSS, no inline styles
- Server Components by default; Client Components only for interactivity
- Better Auth with JWT plugin enabled
- No external UI libraries (no shadcn, radix, framer-motion, etc.)
- No backend / database logic
- No advanced features (due dates, priorities, recurring, filters, sorting, dark mode toggle – but design should be dark-mode friendly)
- Performance: skeleton screens, minimal layout shift, lazy loading hints
- Accessibility: ARIA, keyboard navigation, good contrast
- UX: instant feedback, smooth transitions, no jank, futuristic micro-interactions

## 4. AI-Themed Design System

### Color Palette – Modern AI / Cyber-Tech
- Primary: cyan-400 (#22d3ee) → glowing accents, buttons, links
- Primary-glow: cyan-300/30 → subtle glow/halo effects
- Secondary: purple-500 (#a855f7) → highlights, completed tasks
- Success: emerald-400 (#34d399) → checkmarks, completed state
- Danger: rose-500 (#f43f5e) → delete
- Background: slate-950 (#020617) or gradient from slate-950 to indigo-950
- Surface: slate-900/80 with backdrop-blur-md (glassmorphism)
- Text primary: slate-100
- Text secondary: slate-400
- Border / divider: slate-800 / cyan-900/30
- Glow effect: shadow-[0_0_20px_#22d3ee33] or ring-cyan-400/40

### Typography – Futuristic & Clean
- Headings: font-sans tracking-tight font-bold
- Primary font size scale: text-4xl → text-3xl → text-2xl → text-xl → text-lg → text-base
- Mono for code/task IDs: font-mono text-sm

### Effects & Styles
- Glassmorphism: bg-slate-900/60 backdrop-blur-xl border border-slate-700/50
- Glow: shadow-lg shadow-cyan-500/20 hover:shadow-cyan-400/40 transition-shadow
- Neon accent: bg-gradient-to-r from-cyan-400 to-purple-500
- Hover lift: hover:-translate-y-0.5 transition-transform
- Animated check: scale + rotate + bounce (CSS only)

### Spacing & Layout
- Container: max-w-7xl mx-auto px-4 sm:px-6 lg:px-8
- Card padding: p-6
- Gap: gap-5, gap-6

## 5. Pages & Routes

Public:
- /signup → futuristic centered card with gradient button
- /signin → similar style

Protected:
- / (dashboard) → task grid/list with glowing add button (FAB)
- /tasks/new → modal or full page with neon input focus
- /tasks/[id]/edit → same as new, pre-filled

## 6. Key Components – AI Style

- **Task Card**
  Glass surface, cyan border on hover, glowing completed badge, animated checkbox

- **Add/Edit Modal**
  Centered glass panel, neon focused inputs, gradient submit button

- **Floating Action Button (FAB)**
  Rounded-full, cyan glow, pulse subtle animation when idle

- **Empty State**
  Futuristic illustration + "Initialize your task matrix" text + glowing add button

- **Header**
  Semi-transparent glass bar, cyan accent on active item, logout with hover glow

## 7. Micro-interactions

- Checkbox toggle: scale + cyan pulse + checkmark draw animation
- Button press: scale-95 + glow increase
- Card appear: fade-in + slight slide-up
- New task: neon flash + smooth insert
- Error: red pulse + shake (subtle)

## 8. Centralized API Client (lib/api.ts)

- Auto-attach Bearer token from Better Auth
- Handle 401 → redirect to /signin with toast
- Typed methods: getTasks, createTask, updateTask, deleteTask, toggleComplete
- Return { data, error, isLoading }

## 9. TypeScript Interfaces

```ts
interface Task {
  id: number
  title: string
  description?: string
  completed: boolean
  createdAt: string
  updatedAt: string
}

interface TaskCreateInput {
  title: string
  description?: string
}

interface TaskUpdateInput extends Partial<TaskCreateInput> {
  completed?: boolean
}
10. Acceptance Criteria

Signup / signin / logout works with AI-styled forms
All 5 core features fully functional through UI
Tasks are user-isolated
UI feels futuristic, modern AI dashboard-like
Responsive on all screen sizes
Loading, success, error states are beautiful & clear
No jank, no layout shift, premium feel

11. References

Obey constitution.md
Align with @specs/api/rest-endpoints.md (when created)
Tailwind classes only

This specification provides everything needed to build a visually impressive, AI-themed, modern frontend.
textYou can now use this directly in your Spec-Driven workflow:

```bash
# Save as e.g. specs/ui/frontend-ai-themed-v1.md
# Then reference it:
@specs/ui/frontend-ai-themed-v1.md
Follow constitution.md
Start implementing root layout + auth pages