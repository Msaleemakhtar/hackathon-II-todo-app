# Frontend Implementation Guide

## Constitutional Reference

This guide provides a high-level summary of frontend practices. All development **MUST** adhere to the principles and rules defined in the main constitution at `.specify/memory/constitution.md`.

## Technology Stack & State Management

The technology stack and state management strategy are non-negotiable and are defined in **Section II and VI** of the constitution.
- **Server State:** Use **React Query**.
- **Global State:** Use **Zustand**.
- **Local State:** Use standard React hooks (`useState`).

## Project Structure

This structure is mandated by **Section II** of the constitution.
```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages and layouts
│   ├── components/       # Reusable UI components
│   │   ├── ui/           # Base shadcn/ui components
│   │   └── features/     # Feature-specific components
│   ├── lib/              # Utilities, API client, Zustand stores
│   ├── hooks/            # Custom React hooks
│   └── ...
├── public/               # Static assets
└── package.json
```

## Component Development Standards

- **Organization:** Per **Section VI**, a **feature-based** organization (`/components/features/tasks/...`) is mandatory.
- **Server vs. Client:** Default to Server Components. Use `'use client'` only when interactivity (hooks, event handlers) is required.

## API Integration & Authentication

- **Source of Truth:** The authentication flow is detailed in **Section IV** of the constitution.
- **API Client:** A centralized `axios` instance **MUST** be created in `/lib/api.ts`.
- **Interceptors:** This client **MUST** use interceptors to automatically attach the access token and to handle the token refresh logic on `401 Unauthorized` errors, as specified in the constitution.
- **Environment Variables:** All browser-exposed variables **MUST** be prefixed with `NEXT_PUBLIC_` per **Section VI**.

## User Experience Standards

All UX standards are mandated by **Section VI** of the constitution.
- **Optimistic UI:** Implement optimistic updates for mutations, with rollback on error. This is typically done within a React Query `useMutation` hook.
- **Loading States:** Use skeleton loaders and React Suspense boundaries instead of spinners.
- **User Feedback:** Use non-blocking toast notifications for feedback.
- **Input Optimization:** De-bounce search inputs by 300ms.

## Styling & Accessibility

- **Styling:** Per **Section VI**, styling is handled exclusively with **Tailwind CSS** and **shadcn/ui** components.
- **Accessibility:** WCAG AA compliance is mandatory. Use semantic HTML and provide ARIA labels for all interactive elements.

## Testing and CI/CD

All testing and CI/CD requirements are defined in **Sections VII and IX** of the constitution.

```bash
# Run tests
bun test

# Lint code
bun run lint

# Check TypeScript types
bun run typecheck
```

## Development Workflow

### Package Management (`bun`)
The constitution mandates `bun` for all frontend package management.
```bash
# Install all dependencies
bun install

# Add a new package
bun add <package-name>

# Run the development server
bun dev
```

### Quick Reference
- **Constitutional Authority:** `.specify/memory/constitution.md`
- **State Management:** Zustand (Global), React Query (Server)
- **Component Style:** Feature-based (`/components/features/...`)
- **API Client:** Centralized in `/lib/api.ts`
- **Package Manager:** `bun` only.
