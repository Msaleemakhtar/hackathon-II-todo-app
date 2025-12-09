/sp.specify I need to create a comprehensive task management dashboard UI based on the design in ui.pptx. This should be a
   modern, responsive web application frontend that implements the complete user interface for managing tasks.

   ## Feature Overview
   Create a full-stack frontend application for the task management system with the following key components:

   ### 1. Dashboard Layout
   - **Sidebar Navigation** (coral/salmon colored #FF7B7B)
     - User profile section showing avatar, name, and email
     - Navigation menu items: Dashboard, Vital Task, My Task, Task Categories, Settings, Help
     - Logout button at the bottom

   - **Header Bar**
     - Global search input with placeholder "Search your task here..."
     - Search icon button
     - Notification bell icon
     - User settings icon
     - Current date display (Tuesday 20/06/2023 format)

   - **Main Content Area**
     - Welcome message with user's name and waving hand emoji
     - Team member avatars (showing collaborative users)
     - Invite button for adding team members

   ### 2. Dashboard View Components

   **To-Do Section (Left Panel)**
   - Date-based task grouping showing current date and "Today" label
   - "+ Add task" button
   - Task cards displaying:
     - Task title (e.g., "Attend Nischal's Birthday Party")
     - Task description/details
     - Attached images/thumbnails
     - Priority badges (Moderate, High, Low) with color coding
     - Status indicators (Not Started, In Progress, Completed)
     - Creation date timestamp
     - Three-dot menu for task actions

   **Task Status Dashboard (Right Top Panel)**
   - "Task Status" heading with icon
   - Three circular progress indicators:
     - Completed tasks (84% - green)
     - In Progress tasks (46% - blue)
     - Not Started tasks (13% - gray/red)
   - Legend showing status labels

   **Completed Task Section (Right Bottom Panel)**
   - "Completed Task" heading with checkbox icon
   - List of completed tasks showing:
     - Task title
     - Brief description
     - Completion status badge (green "Completed")
     - Completion timestamp ("Completed 2 days ago")
     - Associated task image
     - Three-dot menu for actions

   ### 3. Technical Requirements

   **Frontend Stack (per Constitution)**
   - Next.js 16 with App Router
   - TypeScript with strict mode
   - shadcn/ui component library for UI elements
   - Tailwind CSS for styling
   - Zustand for state management
   - axios for API calls with JWT interceptors

   **Key Features to Implement**
   1. Responsive design (mobile-first approach)
   2. Optimistic UI updates
   3. Skeleton loading states
   4. Toast notifications for user actions
   5. Search with 300ms debouncing
   6. Filter and sort capabilities
   7. Task CRUD operations via API
   8. JWT authentication integration
   9. Real-time task status updates
   10. Drag-and-drop task management (future enhancement)

   **UI/UX Requirements**
   - Accessible (ARIA labels, keyboard navigation)
   - Color contrast meets WCAG AA standards
   - Smooth animations and transitions
   - Error boundaries for graceful error handling
   - Loading states for all async operations

   **Color Palette**
   - Primary: Coral/Salmon (#FF6B6B or similar)
   - Success: Green (#4CAF50)
   - Info/Progress: Blue (#2196F3)
   - Warning: Orange (#FF9800)
   - Error: Red (#F44336)
   - Background: Light gray (#F5F5F5)
   - Card background: White (#FFFFFF)

   **API Integration Requirements**
   - Connect to existing Task and Tag APIs (from feature 002)
   - Implement JWT token refresh flow
   - Handle authentication states (logged in/out)
   - Scope all data to authenticated user
   - Real-time updates for task completion percentages

   **Performance Targets**
   - First Contentful Paint < 1.5s
   - Time to Interactive < 3s
   - Lighthouse Performance score >= 90

   ### 4. Pages/Routes to Implement
   1. `/` or `/dashboard` - Main dashboard (the design shown)
   2. `/vital-tasks` - Vital/important tasks view
   3. `/my-tasks` - Personal tasks view
   4. `/categories` - Task categories management
   5. `/settings` - User settings
   6. `/help` - Help/support page

   ### 5. Component Breakdown
   - `Sidebar` - Navigation sidebar component
   - `Header` - Top header bar with search and notifications
   - `TaskCard` - Individual task card component
   - `TaskList` - Container for task cards
   - `StatusChart` - Circular progress indicators
   - `CompletedTaskList` - Completed tasks section
   - `SearchBar` - Debounced search input
   - `FilterDropdown` - Filter by status, priority, tags
   - `PriorityBadge` - Priority indicator component
   - `StatusBadge` - Status indicator component
   - `UserAvatar` - User profile avatar component
   - `TeamAvatars` - Avatar group component

   ### 6. State Management (Zustand Stores)
   - `authStore` - User authentication state
   - `taskStore` - Task data and operations
   - `uiStore` - UI state (sidebar, modals, toasts)
   - `filterStore` - Filter and sort preferences

   ### 7. Data Flow
   1. User authenticates → JWT stored → redirected to dashboard
   2. Dashboard loads → fetch user tasks from API
   3. Display tasks in appropriate sections (pending/completed)
   4. Calculate status percentages for charts
   5. User interacts → optimistic UI update → API call → sync on response
   6. Real-time updates via periodic polling or WebSocket (future)

   ### 8. Acceptance Criteria
   - [ ] User can view all their tasks in the dashboard
   - [ ] Tasks display with correct title, description, priority, and status
   - [ ] Task status percentages calculate and display correctly
   - [ ] User can search tasks and see filtered results
   - [ ] User can filter tasks by status, priority, and tags
   - [ ] User can create new tasks via "+ Add task" button
   - [ ] User can edit tasks via three-dot menu
   - [ ] User can delete tasks with confirmation
   - [ ] User can mark tasks as complete/incomplete
   - [ ] Completed tasks appear in the completed section
   - [ ] UI is responsive on mobile, tablet, and desktop
   - [ ] All interactions show loading states
   - [ ] Errors display user-friendly toast messages
   - [ ] Navigation between sections works smoothly
   - [ ] User profile displays correct name and email

   ### 9. Out of Scope for This Feature
   - Team collaboration features (invite functionality UI only, no backend)
   - Task attachments/file uploads
   - Recurring task UI
   - Calendar view
   - Gantt chart or timeline views
   - Export/import functionality
   - Dark mode (can be added later)

   ### 10. Dependencies
   - Feature 001: Foundational backend setup (completed)
   - Feature 002: Task and Tag API (completed)
   - User authentication system (needs to be implemented or referenced)
   Create or update the feature specification from a natural language feature description. (project)
