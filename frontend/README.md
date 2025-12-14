# Todo App Frontend

This is the frontend for the Todo App, built with Next.js 16, React 19, TypeScript, and Better Auth. This project follows **Spec-Driven Development (SDD)** principles as defined in the [Phase II Constitution](../.specify/memory/constitution.md).

## Features

### Core Features
- **Better Auth Integration** - Full authentication flow with session management and PostgreSQL storage
- **JWT Token Management** - Automatic token generation and refresh for backend API calls
- **Task Dashboard** - Visual overview of tasks with status charts and quick actions
- **Task Management** - Create, update, delete, and filter tasks with priority levels and status tracking
- **Category System** - Organize tasks into categories for better organization
- **Tag System** - Organize tasks with custom tags and colors for flexible categorization
- **Reminder System** - Set reminders for tasks with customizable notification times
- **Drag & Drop** - Reorder tasks with intuitive drag-and-drop interface
- **Virtualized Lists** - High-performance rendering for large task lists
- **Responsive Design** - Mobile-first UI built with Tailwind CSS and shadcn/ui components
- **Real-time State Management** - Client-side state with Zustand
- **Protected Routes** - Automatic authentication and route protection with HOC
- **Type-Safe API Client** - Axios-based client with TypeScript types and automatic JWT injection

### Advanced Features
- **Progressive Web App (PWA)** - Installable app with offline support and native-like experience
- **Push Notifications** - Browser push notifications for task reminders
- **Offline Mode** - Full offline functionality with background sync
- **Keyboard Shortcuts** - Efficient navigation and task management with hotkeys
- **Performance Monitoring** - Core Web Vitals tracking and analytics
- **Error Tracking** - Sentry integration for production error monitoring
- **Analytics** - Privacy-first user interaction tracking with opt-out support
- **Service Worker** - Background sync, offline caching, and push notification support

## Constitutional Reference

All frontend development **MUST** adhere to the principles defined in:
- **Main Constitution**: `../.specify/memory/constitution.md`
- **Better Auth Integration Guide**: `../BETTER_AUTH_IMPLEMENTATION.md`

## Setup

### Prerequisites

- **Node.js** 20+ (LTS recommended)
- **Bun** 1.0+ (package manager - **required**)
- **Backend API** running on `http://localhost:8000` (see `../backend/README.md`)
- **PostgreSQL database** (same as backend, for Better Auth sessions)

### Local Development Setup

1. **Navigate to the frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies using Bun:**

   ```bash
   bun install
   ```

3. **Environment Configuration:**

   Create `.env.local` file in the frontend directory:

   ```bash
   # Copy the example (if available) or create new
   touch .env.local
   ```

   Add the following environment variables:

   ```bash
   # API Configuration
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
   NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000

   # Better Auth Configuration (must match backend)
   BETTER_AUTH_SECRET=your-very-secure-jwt-secret-key-here-min-32-chars

   # Database URL (PostgreSQL - same as backend)
   # For Neon Serverless PostgreSQL, include ?sslmode=require
   DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require

   # Error Monitoring (Sentry) - Optional, production only
   NEXT_PUBLIC_SENTRY_DSN=https://your-client-sentry-dsn@sentry.io/project-id
   SENTRY_DSN=https://your-server-sentry-dsn@sentry.io/project-id
   SENTRY_ORG=your-sentry-org
   SENTRY_PROJECT=your-sentry-project

   # PWA Configuration - Optional
   NEXT_PUBLIC_VAPID_PUBLIC_KEY=your-vapid-public-key-from-backend
   ```

   **⚠️ CRITICAL:**
   - `BETTER_AUTH_SECRET` must match the value in `backend/.env`
   - `NEXT_PUBLIC_VAPID_PUBLIC_KEY` should match the value from backend's `/api/v1/subscriptions/vapid-public-key` endpoint

### Database Initialization (Better Auth Tables)

Better Auth requires database tables for users, sessions, and accounts. Run the initialization script:

```bash
bun run scripts/init-better-auth-db.ts
```

This creates the following tables:
- `user` - User profiles (id, email, name, timestamps)
- `account` - Authentication credentials (password hashes)
- `session` - Active user sessions
- `verification` - Email verification tokens (optional)

**Note:** These tables are separate from the backend's task/tag tables. They share the same PostgreSQL database but use a different namespace.

### Run the Development Server

```bash
bun run dev
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Login**: http://localhost:3000/login
- **Signup**: http://localhost:3000/signup
- **Dashboard**: http://localhost:3000/dashboard (protected)

The page auto-reloads when you edit files.

## Application Structure

### Pages & Routes

- `/` - Landing page with login/signup options
- `/login` - User login page
- `/signup` - User registration page
- `/dashboard` - Main dashboard with task overview and charts (protected)
- `/my-tasks` - Personal task list with filtering and sorting (protected)
- `/vital-tasks` - High-priority and due-soon tasks (protected)
- `/categories` - Tag management and task organization (protected)
- `/settings` - User profile and preferences (protected)
- `/help` - Application help and documentation (protected)

**Route Protection:** All routes except `/`, `/login`, and `/signup` require authentication. Unauthenticated users are automatically redirected to `/login`.

### API Routes

- `/api/auth/[...all]` - Better Auth server endpoints (signup, signin, signout, session management)
- `/api/auth/token` - Custom JWT token generation for backend API calls

## Better Auth Integration Flow

The frontend uses **Better Auth** for authentication with custom JWT token integration for backend API calls.

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                    BETTER AUTH AUTHENTICATION FLOW                    │
└──────────────────────────────────────────────────────────────────────┘

  User Action                Frontend (Next.js)              Backend (FastAPI)
  ───────────                ──────────────────              ─────────────────

1. Sign Up / Log In
      │
      ├──> POST /api/auth/signup
      │    POST /api/auth/signin
      │    (Better Auth Server)
      │         │
      │         ├──> Hash Password (bcrypt)
      │         ├──> Create User Record ──────> PostgreSQL [user table]
      │         ├──> Create Session ──────────> PostgreSQL [session table]
      │         └──> Set Session Cookie
      │              (HTTP-only, Secure, SameSite)
      │
      │<─── Session Cookie (7 days)
      │

2. Access Protected Page
      │
      ├──> Check Session
      │    (Better Auth Client)
      │         │
      │         ├──> Read Session Cookie
      │         ├──> Verify Session ─────────> PostgreSQL [session table]
      │         └──> Get User Data
      │
      │<─── User Profile {id, email, name}
      │

3. Make API Call (e.g., Fetch Tasks)
      │
      ├──> GET /my-tasks (React Component)
      │         │
      │         ├──> useTasks() hook
      │         └──> apiClient.get('/api/v1/tasks')
      │                   │
      │                   ├──> Axios Request Interceptor
      │                   │         │
      │                   │         ├──> GET /api/auth/token
      │                   │         │    (Custom JWT Endpoint)
      │                   │         │         │
      │                   │         │         ├──> Verify Better Auth Session
      │                   │         │         ├──> Generate JWT Token
      │                   │         │         │    - user_id (Better Auth ID)
      │                   │         │         │    - email
      │                   │         │         │    - exp (15 min)
      │                   │         │         └──> Sign with BETTER_AUTH_SECRET
      │                   │         │
      │                   │         │<─── JWT Token
      │                   │         │
      │                   │         └──> Add Header:
      │                   │              Authorization: Bearer <JWT>
      │                   │
      │                   └──> GET /api/v1/tasks ───────────────────────────>
      │                        Header: Authorization: Bearer <JWT>
      │                                                                    │
      │                                                                    ├──> Verify JWT
      │                                                                    │    (python-jose)
      │                                                                    │    - Check signature
      │                                                                    │    - Validate expiry
      │                                                                    │    - Extract user_id
      │                                                                    │
      │                                                                    ├──> Query Tasks
      │                                                                    │    WHERE user_id = <from_jwt>
      │                                                                    │
      │                   <──────────────────────────────────────────────-┘
      │<─── Tasks Data                                                Response: User's tasks only
      │     Display in UI
      │

4. Logout
      │
      ├──> POST /api/auth/signout
      │    (Better Auth Server)
      │         │
      │         ├──> Delete Session ─────────> PostgreSQL [session table]
      │         └──> Clear Session Cookie
      │
      │<─── Redirect to /login
      │


┌──────────────────────────────────────────────────────────────────────┐
│                            KEY COMPONENTS                             │
└──────────────────────────────────────────────────────────────────────┘

Better Auth (Frontend):
  • User authentication (signup, signin, signout)
  • Session management (PostgreSQL storage)
  • Session cookies (HTTP-only, Secure, SameSite=Lax)
  • User profile management
  • CSRF protection

JWT Token Bridge (Custom):
  • Endpoint: /api/auth/token (Next.js API route)
  • Generates JWT from Better Auth session
  • Signs with BETTER_AUTH_SECRET (shared with backend)
  • 15-minute token expiry
  • Contains: user_id, email, exp

Axios Interceptor (Frontend):
  • Automatically fetches JWT before API calls
  • Adds Authorization header
  • Handles token refresh on 401 errors
  • Caches token until expiry

Backend Validation (FastAPI):
  • Validates JWT signature and expiry
  • Extracts user_id from token
  • Enforces data isolation (all queries scoped to user_id)
  • No session storage (stateless)

Database Tables:
  • Better Auth: user, session, account, verification
  • App Data: tasks, categories, tags, task_tag_link
  • All share same PostgreSQL database
```

### Token Lifecycle

```
Better Auth Session (Primary Auth)
├─ Created: On signup/signin
├─ Storage: PostgreSQL + HTTP-only cookie
├─ Expiry: 7 days (default)
└─ Used for: Page authentication, JWT generation

JWT Token (Backend API Auth)
├─ Created: On-demand per API request
├─ Storage: None (generated fresh, not cached)
├─ Expiry: 15 minutes
├─ Used for: Backend API authorization
└─ Contains: {user_id, email, exp}
```

### Security Features

1. **Dual-Layer Authentication**
   - Better Auth for user sessions (frontend)
   - JWT for API calls (backend validation)

2. **Session Security**
   - HTTP-only cookies (no JavaScript access)
   - Secure flag (HTTPS only in production)
   - SameSite=Lax (CSRF protection)

3. **Token Security**
   - Short-lived JWT (15 min expiry)
   - Signed with BETTER_AUTH_SECRET
   - Automatic refresh on API calls

4. **Data Isolation**
   - All API queries scoped to authenticated user_id
   - 404 Not Found for unauthorized access (no information leakage)

5. **Environment Security**
   - Secrets stored in .env.local
   - BETTER_AUTH_SECRET shared between frontend and backend
   - Database connection string with SSL for production

See [BETTER_AUTH_IMPLEMENTATION.md](../BETTER_AUTH_IMPLEMENTATION.md) for detailed architecture and security model.

## Key Components

### Layout Components

**`src/components/layout/Header.tsx`**
- Top navigation bar with user menu
- Search functionality
- Logout action

**`src/components/layout/Sidebar.tsx`**
- Main navigation menu
- Active route highlighting
- Task count badges

### Task Components

**`src/components/tasks/TaskList.tsx`**
- Display list of tasks with filters
- Infinite scroll or pagination
- Quick actions (complete, edit, delete)

**`src/components/tasks/TaskCard.tsx`**
- Individual task display
- Priority badges
- Tag chips
- Due date indicators

**`src/components/tasks/CreateTaskModal.tsx`**
- Modal for creating new tasks
- Form validation
- Tag selection

**`src/components/tasks/TaskDetailModal.tsx`**
- Detailed task view
- Edit functionality
- Tag management

**`src/components/tasks/DraggableTaskList.tsx`**
- Drag-and-drop task reordering
- Visual feedback during drag operations
- Optimistic UI updates

**`src/components/tasks/VirtualizedTaskList.tsx`**
- High-performance virtualized rendering
- Handles thousands of tasks efficiently
- Windowing for memory optimization

**`src/components/tasks/ReminderSelector.tsx`**
- Visual reminder time selection
- Preset options (1h, 1d, 1w before due date)
- Custom date/time picker

**`src/components/tasks/SortableTaskCard.tsx`**
- Task card with drag-and-drop support
- Priority and status indicators
- Quick actions (complete, edit, delete)

### Dashboard Components

**`src/components/dashboard/TaskStatusChart.tsx`**
- Visual representation of task completion
- Progress bars and statistics
- Priority breakdown

### Authentication Components

**`src/components/auth/LoginForm.tsx`**
- Email/password login form
- Better Auth integration
- Error handling

**`src/components/auth/RegistrationForm.tsx`**
- User signup form
- Password validation
- Email verification (optional)

### PWA & Advanced Components

**`src/components/PWAInstallPrompt.tsx`**
- Custom PWA installation UI
- Dismissible prompt with 7-day timeout
- Auto-hides if app is already installed
- Responsive design for mobile and desktop

**`src/components/OfflineIndicator.tsx`**
- Network status indicator
- Visual feedback when offline
- Background sync status

**`src/components/KeyboardShortcutsHelp.tsx`**
- Keyboard shortcuts reference modal
- Context-sensitive help
- Searchable shortcut list

**`src/components/notifications/NotificationPermissionPrompt.tsx`**
- Push notification permission request UI
- Educational messaging
- One-time dismissal

**`src/components/notifications/NotificationSettings.tsx`**
- Notification preferences management
- Subscribe/unsubscribe controls
- Test notification button

### UI Components (shadcn/ui)

Located in `src/components/ui/`:
- `button.tsx` - Button component with variants
- `card.tsx` - Card container
- `dialog.tsx` - Modal dialogs
- `input.tsx` - Form inputs
- `checkbox.tsx` - Checkbox component
- `dropdown-menu.tsx` - Dropdown menus
- `badge.tsx` - Status badges
- `avatar.tsx` - User avatar
- `progress.tsx` - Progress bars
- `tabs.tsx` - Tab navigation
- `label.tsx` - Form labels
- `table.tsx` - Data tables
- `calendar.tsx` - Date picker calendar
- `popover.tsx` - Popover component
- `radio-group.tsx` - Radio button groups
- `textarea.tsx` - Multi-line text input

## State Management

### Zustand Stores

**`src/store/ui-store.ts`**
- UI state (modals, sidebars, loading states)
- Theme preferences
- Filter/sort settings

**Example Usage:**
```typescript
import { useUIStore } from '@/store/ui-store';

const { isCreateModalOpen, setCreateModalOpen } = useUIStore();
```

### Custom Hooks

**`src/hooks/useAuth.ts`**
- Authentication state management
- Login/logout functions
- User profile access
- Session validation

**`src/hooks/useTasks.ts`**
- Task fetching and caching
- CRUD operations
- Optimistic updates
- Error handling

**`src/hooks/useCategories.ts`**
- Category fetching and management
- Create, update, delete categories
- Category-based task filtering

**`src/hooks/useTags.ts`**
- Tag fetching and management
- Create, update, delete tags
- Tag-based task filtering

**`src/hooks/useAnalytics.ts`**
- General event tracking with privacy controls
- Pre-defined task events (created, completed, deleted, reordered)
- Opt-in/opt-out functionality
- PII filtering and development environment filtering

**`src/hooks/useNotifications.ts`**
- Web Push notification subscription management
- Permission request handling
- Subscription lifecycle (subscribe, unsubscribe, update)
- VAPID key integration

**`src/hooks/useKeyboardShortcuts.ts`**
- Global keyboard shortcut registration
- Context-aware hotkeys
- Customizable key bindings

**`src/hooks/useOffline.ts`**
- Network status detection
- Offline/online state management
- Background sync coordination

**`src/hooks/useDebounce.ts`**
- Input debouncing for search and filters
- Performance optimization for expensive operations

## API Integration

### API Client (`src/lib/api-client.ts`)

Pre-configured Axios instance with:
- Base URL from environment
- JWT token interceptor (automatic)
- Error handling and retries
- Request/response transformations

**Example Usage:**
```typescript
import { apiClient } from '@/lib/api-client';

// Automatically includes JWT token
const tasks = await apiClient.get('/tasks');
const newTask = await apiClient.post('/tasks', taskData);
```

### Type Definitions (`src/types/index.ts`)

TypeScript interfaces for:
- `User` - User profile structure
- `Task` - Task entity with all fields (including status and category)
- `Category` - Category entity with description and color
- `Tag` - Tag entity with color
- `TaskCreateInput` / `TaskUpdateInput` - Request payloads
- `CategoryCreateInput` / `CategoryUpdateInput` - Category payloads
- `TagCreateInput` / `TagUpdateInput` - Tag payloads
- `PaginatedResponse<T>` - Paginated API responses
- `TaskStatus` - "pending" | "in_progress" | "completed"
- `TaskPriority` - "low" | "medium" | "high"

## Styling

### Tailwind CSS

- **Configuration**: `tailwind.config.ts`
- **Global Styles**: `src/app/globals.css`
- **Theme**: Customizable color palette, dark mode support
- **Utilities**: Custom utility classes for common patterns

### Design System

- **Colors**: Primary, secondary, accent, neutral shades
- **Typography**: Responsive font sizes, line heights
- **Spacing**: Consistent spacing scale (4px base unit)
- **Breakpoints**: Mobile-first responsive design
  - `sm`: 640px
  - `md`: 768px
  - `lg`: 1024px
  - `xl`: 1280px
  - `2xl`: 1536px

## Development Workflow

### Common Commands

```bash
# Start development server
bun run dev

# Build for production
bun run build

# Start production server
bun run start

# Run linter
bun run lint

# Type checking (if configured)
bun run type-check

# Initialize Better Auth database tables
bun run scripts/init-better-auth-db.ts
```

### Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | Yes | Backend API base URL | `http://localhost:8000/api` |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | Yes | Frontend URL for Better Auth | `http://localhost:3000` |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret (matches backend) | `b3tterAuthS3cretThatsAtL3ast32CharsLong!` |
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://user:pass@host:5432/db?sslmode=require` |

**Note:** Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser. Keep secrets (like `BETTER_AUTH_SECRET`) without this prefix.

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── auth/
│   │   │       ├── [...all]/route.ts   # Better Auth server routes
│   │   │       └── token/route.ts      # JWT token generation
│   │   ├── dashboard/page.tsx          # Dashboard page
│   │   ├── login/page.tsx              # Login page
│   │   ├── signup/page.tsx             # Signup page
│   │   ├── my-tasks/page.tsx           # Task list page
│   │   ├── vital-tasks/page.tsx        # High-priority tasks
│   │   ├── categories/page.tsx         # Tag management
│   │   ├── settings/page.tsx           # User settings
│   │   ├── help/page.tsx               # Help documentation
│   │   ├── layout.tsx                  # Root layout with providers
│   │   ├── page.tsx                    # Landing page
│   │   └── globals.css                 # Global styles
│   ├── components/
│   │   ├── auth/                       # Authentication components
│   │   ├── dashboard/                  # Dashboard components
│   │   ├── layout/                     # Header, Sidebar, Footer
│   │   ├── tasks/                      # Task-related components
│   │   ├── ui/                         # shadcn/ui components
│   │   └── withAuth.tsx                # HOC for route protection
│   ├── hooks/
│   │   ├── useAuth.ts                  # Authentication hook
│   │   └── useTasks.ts                 # Task management hook
│   ├── lib/
│   │   ├── api-client.ts               # Axios instance with interceptors
│   │   ├── auth.ts                     # Better Auth client config
│   │   └── utils.ts                    # Utility functions
│   ├── store/
│   │   └── ui-store.ts                 # Zustand UI state store
│   └── types/
│       └── index.ts                    # TypeScript type definitions
├── scripts/
│   └── init-better-auth-db.ts          # Better Auth DB initialization
├── public/                             # Static assets
├── .env.local                          # Environment variables (not committed)
├── .eslintrc.json                      # ESLint configuration
├── next.config.js                      # Next.js configuration
├── package.json                        # Dependencies and scripts
├── postcss.config.js                   # PostCSS configuration
├── tailwind.config.ts                  # Tailwind CSS configuration
├── tsconfig.json                       # TypeScript configuration
└── README.md                           # This file
```

## Key Dependencies

### Core Framework
- **`next@16.0.8`** - React framework with App Router, server components, and API routes
- **`react@19.2.1`** - UI library (v19 with improved hooks and concurrent features)
- **`react-dom@19.2.1`** - React DOM renderer
- **`typescript@5`** - Type safety and developer experience

### Authentication & Security
- **`better-auth@1.4.6`** - Modern authentication library for Next.js with PostgreSQL support
- **`jose@6.1.3`** - JWT signing and verification (used for backend API tokens)
- **`pg@8.16.3`** - PostgreSQL client for Better Auth session storage
- **`bcrypt`** - Password hashing (via Better Auth)

### UI Components & Styling
- **`tailwindcss@3.4.17`** - Utility-first CSS framework
- **`@radix-ui/*`** - Headless UI components (dialog, dropdown, checkbox, etc.)
- **`class-variance-authority@0.7.1`** - CSS class composition
- **`clsx@2.1.1`** - Conditional class names
- **`tailwind-merge@2.5.5`** - Merge Tailwind classes
- **`tailwindcss-animate@1.0.7`** - Animation utilities
- **`lucide-react@0.556.0`** - Icon library

### State Management & API
- **`zustand@5.0.9`** - Lightweight state management
- **`axios@1.13.2`** - HTTP client for API calls
- **`date-fns@4.1.0`** - Date manipulation and formatting

### Development Tools
- **`eslint@9`** - Code linting
- **`eslint-config-next@16.0.8`** - Next.js ESLint config
- **`autoprefixer@10.4.20`** - CSS vendor prefixing
- **`postcss@8.4.49`** - CSS processing

## Progressive Web App (PWA) Features

### Installation

The app can be installed as a Progressive Web App on supported browsers:

1. **Desktop (Chrome, Edge)**:
   - Visit the site and look for the install prompt in the address bar
   - Or use the custom install prompt that appears automatically
   - Click "Install" to add the app to your desktop

2. **Android (Chrome)**:
   - Visit the site and tap the "Add to Home Screen" prompt
   - Or use the browser menu → "Install app"
   - The app will appear on your home screen like a native app

3. **iOS (Safari)**:
   - Visit the site and tap the Share button
   - Scroll down and tap "Add to Home Screen"
   - Confirm to add the app icon to your home screen

### PWA Features

**Offline Support:**
- Tasks cached for offline viewing
- Create, edit, and delete tasks while offline
- Automatic sync when connection is restored
- Offline fallback page for unavailable resources

**App Shortcuts:**
- Quick access to common actions from app icon
- "New Task" - Create a task immediately
- "Search Tasks" - Open search interface

**Standalone Mode:**
- Runs in its own window without browser UI
- Custom splash screen
- Native app-like experience

**Push Notifications:**
- Browser push notifications for task reminders
- Permission-based (user opt-in required)
- Works even when app is closed
- Configurable notification times

### Keyboard Shortcuts

Press `?` or `Ctrl+/` to view all shortcuts. Common shortcuts include:

| Shortcut | Action |
|----------|--------|
| `N` or `Ctrl+N` | Create new task |
| `S` or `Ctrl+K` | Search tasks |
| `?` or `Ctrl+/` | Show keyboard shortcuts help |
| `Esc` | Close modals/dialogs |
| `↑` / `↓` | Navigate task list |
| `Enter` | Open selected task |
| `E` | Edit selected task |
| `D` | Delete selected task |
| `Space` | Toggle task completion |

### Analytics & Privacy

**Performance Tracking:**
- Core Web Vitals (LCP, FID, CLS, INP, TTFB, FCP, TBT)
- Automatic reporting to backend analytics endpoint
- Helps identify and fix performance issues

**Event Tracking:**
- User interactions (task created, completed, deleted, etc.)
- Privacy-first approach (no PII collected)
- Automatic consent management
- Easy opt-out via settings

**Opt-Out:**
```typescript
import { useAnalytics } from '@/hooks/useAnalytics';

const { optOut, optIn, hasConsent } = useAnalytics();

// Check consent status
console.log(hasConsent); // true/false

// Opt out of analytics
optOut();

// Opt back in
optIn();
```

## Testing the Application

### 1. Start the Backend

Ensure the backend API is running (see `../backend/README.md`):

```bash
cd ../backend
uv run uvicorn src.main:app --reload --port 8000
```

### 2. Start the Frontend

```bash
cd frontend
bun run dev
```

### 3. Test User Registration

1. Navigate to http://localhost:3000/signup
2. Fill in registration form:
   - Name: "Test User"
   - Email: "test@example.com"
   - Password: "password123"
3. Click "Register"
4. Should redirect to login page

### 4. Test User Login

1. Navigate to http://localhost:3000/login
2. Enter credentials:
   - Email: "test@example.com"
   - Password: "password123"
3. Click "Sign In"
4. Should redirect to dashboard at http://localhost:3000/dashboard

### 5. Test Task Management

1. Click "Create Task" button
2. Fill in task details:
   - Title: "Complete project"
   - Description: "Finish the todo app"
   - Priority: "high"
   - Due Date: Select future date
3. Add tags if desired
4. Click "Create"
5. Task should appear in task list

### 6. Verify API Authentication

Open browser DevTools (F12) → Network tab:
1. Make any API call (create task, fetch tasks)
2. Check request headers:
   - Should contain: `Authorization: Bearer <jwt-token>`
3. Check response:
   - Status: 200 OK
   - Data should contain only your tasks

### 7. Test Route Protection

1. Logout from the application
2. Try to access http://localhost:3000/dashboard
3. Should be redirected to http://localhost:3000/login

## Troubleshooting

### Common Issues

**1. "Connection is insecure" Database Error**
```bash
# Ensure DATABASE_URL includes SSL mode for Neon
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

**2. API Calls Return 401 Unauthorized**
```bash
# Verify BETTER_AUTH_SECRET matches between frontend and backend
# Frontend: .env.local
# Backend: .env

# Should be identical
BETTER_AUTH_SECRET=b3tterAuthS3cretThatsAtL3ast32CharsLong!
```

**3. Session Not Persisting**
- Clear browser cookies and local storage
- Restart development server
- Re-login

**4. Port Already in Use**
```bash
# Kill process using port 3000
lsof -ti:3000 | xargs kill -9

# Or use a different port
bun run dev --port 3001
```

**5. Better Auth Tables Missing**
```bash
# Run the initialization script
bun run scripts/init-better-auth-db.ts

# Verify tables exist in database
psql $DATABASE_URL -c "\dt"
```

**6. "relation 'session' does not exist" Error**
If you encounter this error in the logs, it means the Better Auth tables were not created:

```bash
# Initialize Better Auth tables in the database
bun run scripts/init-better-auth-db.ts

# Verify the tables were created
psql $DATABASE_URL -c "\dt" | grep -E "(user|account|session|verification)"
```

**7. PostgreSQL Reserved Keyword Issues**
If you encounter errors like `relation "user" does not exist`, this may be due to the reserved PostgreSQL keyword "user". The Better Auth tables are defined with proper quoting to handle this:

```sql
CREATE TABLE "user" (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  "emailVerified" BOOLEAN NOT NULL DEFAULT false,
  name TEXT,
  "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
  "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
);
```

When creating custom queries involving these tables, ensure you quote the table names properly:
- Use `"user"` instead of `user`
- This prevents PostgreSQL from treating it as a reserved keyword
- Apply the same quoting to column names that might conflict with keywords (like "user"."email")

**7. JWT Token Errors**
- Check browser console for errors
- Verify `NEXT_PUBLIC_API_BASE_URL` is correct
- Ensure backend is running and accessible
- Check Network tab for failed `/api/auth/token` calls

**8. TypeScript Errors**
```bash
# Clean Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules
bun install

# Restart dev server
bun run dev
```

**9. Sentry Not Capturing Errors**
```bash
# Verify Sentry DSN is set
echo $NEXT_PUBLIC_SENTRY_DSN
echo $SENTRY_DSN

# Check environment
echo $NEXT_PUBLIC_ENVIRONMENT

# Ensure errors are only sent in production
# Development errors are filtered out by default
```

**10. PWA Not Installing**
- Check browser console for manifest errors
- Verify all required icons exist in `public/icons/`
- Ensure HTTPS is enabled (required for PWA in production)
- Check service worker registration in DevTools → Application
- Verify manifest at `/manifest.webmanifest` is accessible

**11. Push Notifications Not Working**
```bash
# Verify VAPID public key is set
echo $NEXT_PUBLIC_VAPID_PUBLIC_KEY

# Check browser permissions
# DevTools → Application → Storage → Permissions

# Verify service worker is registered
# DevTools → Application → Service Workers

# Test notification permission
navigator.permissions.query({name: 'notifications'})
```

**12. Offline Mode Not Working**
- Check service worker is active (DevTools → Application → Service Workers)
- Verify cache storage has entries (DevTools → Application → Cache Storage)
- Enable offline mode in DevTools → Network tab to test
- Check background sync status in DevTools → Application → Background Sync

## Performance Optimization

### Build Optimization

Next.js automatically optimizes the production build:
- **Code Splitting** - Automatic route-based splitting
- **Image Optimization** - `next/image` for optimized images
- **Font Optimization** - `next/font` for web font optimization
- **Bundle Analysis** - Run `ANALYZE=true bun run build` (if configured)

### Best Practices

1. **Use Server Components** - Reduce client-side JavaScript
2. **Optimize Images** - Always use `next/image`
3. **Lazy Load Components** - Use dynamic imports for heavy components
4. **Minimize Client-Side State** - Prefer server-side data fetching
5. **Cache API Responses** - Implement request caching where appropriate

## Deployment

### Environment Setup

1. Set production environment variables in your hosting platform
2. Ensure `BETTER_AUTH_SECRET` is securely stored
3. Update `NEXT_PUBLIC_API_BASE_URL` to production backend URL
4. Configure `DATABASE_URL` to production PostgreSQL instance

### Build for Production

```bash
bun run build
```

### Deployment Platforms

**Vercel (Recommended for Next.js):**
1. Connect GitHub repository
2. Configure environment variables
3. Deploy automatically on push to main branch

**Docker:**
```bash
# Build image
docker build -t todo-frontend:latest .

# Run container
docker run -p 3000:3000 todo-frontend:latest
```

**Other Platforms:**
- Netlify
- AWS Amplify
- Google Cloud Run
- DigitalOcean App Platform

### Production Checklist

- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] Better Auth tables initialized
- [ ] CORS origins updated in backend
- [ ] SSL/HTTPS enabled
- [ ] Error monitoring configured (Sentry, etc.)
- [ ] Analytics configured (if needed)
- [ ] Performance monitoring enabled

## Architecture & Design Patterns

### Component Architecture

- **Server Components** - Default for pages and layouts (Next.js 13+ App Router)
- **Client Components** - Interactive components marked with `'use client'`
- **Composition** - Small, reusable components over large monolithic ones
- **Props vs Context** - Props for component data, Context for global state

### Data Fetching Strategy

- **Server-Side Rendering (SSR)** - Pages that need fresh data on every request
- **Static Generation (SSG)** - Pages that can be pre-rendered at build time
- **Client-Side Fetching** - Interactive data that changes frequently
- **Hybrid Approach** - Combine SSR with client-side mutations

### Authentication Pattern

- **Better Auth Server** - Handles all authentication logic server-side
- **JWT Tokens** - Stateless authentication for API calls
- **Session Cookies** - Secure, HTTP-only cookies for Better Auth sessions
- **Automatic Refresh** - Axios interceptor handles token refresh transparently

### Security Best Practices

- **Environment Variables** - Never commit `.env.local`
- **HTTPS Only** - Enforce SSL in production
- **CORS Configuration** - Strict origin validation on backend
- **XSS Prevention** - React's built-in escaping + CSP headers
- **CSRF Protection** - Better Auth includes CSRF tokens
- **Input Validation** - Client and server-side validation

## Getting Help

- **Phase II Constitution**: `../.specify/memory/constitution.md`
- **Better Auth Guide**: `../BETTER_AUTH_IMPLEMENTATION.md`
- **Backend API Docs**: http://localhost:8000/docs (Swagger UI)
- **ADRs**: `../history/adr/` for architectural decisions
- **Next.js Documentation**: https://nextjs.org/docs
- **Better Auth Documentation**: https://www.better-auth.com/docs

---

**Frontend Version**: 0.1.0
**Last Updated**: 2025-12-11
**Status**: ✅ Ready for Development
