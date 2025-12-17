# API Client with Better Auth Integration

Complete guide for implementing API client with automatic JWT token management and Better Auth session handling.

## Overview

The API client handles:
- Session validation before API calls
- JWT token generation and caching
- Automatic token attachment to requests
- Token refresh on 401 errors
- Sign out on authentication failure

## Installation

```bash
cd frontend
bun add axios
```

## Implementation

### 1. Token Cache Module

Create `lib/token-cache.ts`:

```ts
interface CachedToken {
  token: string;
  expiresAt: number;
}

class TokenCache {
  private cache: CachedToken | null = null;
  private fetchPromise: Promise<string> | null = null;

  /**
   * Get cached token or fetch new one
   */
  async getToken(sessionCheck: () => Promise<boolean>): Promise<string | null> {
    // Return cached token if valid
    if (this.cache && this.isTokenValid(this.cache.expiresAt)) {
      return this.cache.token;
    }

    // Prevent duplicate fetch requests
    if (this.fetchPromise) {
      return this.fetchPromise;
    }

    // Verify session exists
    const hasSession = await sessionCheck();
    if (!hasSession) {
      this.clear();
      return null;
    }

    // Fetch new token
    this.fetchPromise = this.fetchNewToken();

    try {
      const token = await this.fetchPromise;
      return token;
    } finally {
      this.fetchPromise = null;
    }
  }

  /**
   * Fetch fresh JWT token from backend
   */
  private async fetchNewToken(): Promise<string> {
    const response = await fetch('/api/auth/token', {
      credentials: 'include', // Include session cookies
    });

    if (!response.ok) {
      throw new Error(`Token fetch failed: ${response.status}`);
    }

    const data = await response.json();

    // Cache token with 3-minute buffer
    this.cache = {
      token: data.token,
      expiresAt: data.expiresAt,
    };

    return data.token;
  }

  /**
   * Check if token is still valid (with buffer)
   */
  private isTokenValid(expiresAt: number): boolean {
    const bufferMs = 3 * 60 * 1000; // 3 minutes
    return Date.now() + bufferMs < expiresAt;
  }

  /**
   * Clear cached token
   */
  clear() {
    this.cache = null;
    this.fetchPromise = null;
  }
}

export const tokenCache = new TokenCache();
```

### 2. Session Cache Module

Create `lib/session-cache.ts`:

```ts
import { getSession } from './auth';

interface SessionCache {
  hasSession: boolean;
  timestamp: number;
}

class SessionCacheManager {
  private cache: SessionCache | null = null;
  private readonly TTL = 60 * 1000; // 60 seconds

  /**
   * Check if user has valid Better Auth session
   */
  async hasSession(): Promise<boolean> {
    // Return cached result if fresh
    if (this.cache && Date.now() - this.cache.timestamp < this.TTL) {
      return this.cache.hasSession;
    }

    // Check session with Better Auth
    try {
      const session = await getSession();
      const hasSession = !!session?.user;

      // Cache result
      this.cache = {
        hasSession,
        timestamp: Date.now(),
      };

      return hasSession;
    } catch (error) {
      return false;
    }
  }

  /**
   * Clear session cache
   */
  clear() {
    this.cache = null;
  }
}

export const sessionCache = new SessionCacheManager();
```

### 3. API Client

Create `lib/api-client.ts`:

```ts
import axios, { AxiosInstance, AxiosError } from 'axios';
import { tokenCache } from './token-cache';
import { sessionCache } from './session-cache';
import { signOut } from './auth';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies for Better Auth
});

/**
 * Request interceptor: Attach JWT token
 */
apiClient.interceptors.request.use(
  async (config) => {
    try {
      // Check if session exists
      const hasSession = await sessionCache.hasSession();

      if (!hasSession) {
        console.warn('No active session found');
        return config;
      }

      // Get JWT token (cached or fresh)
      const token = await tokenCache.getToken(() => sessionCache.hasSession());

      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Failed to attach token:', error);
    }

    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Response interceptor: Handle auth errors
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      // Clear cached token
      tokenCache.clear();
      sessionCache.clear();

      // Try to refresh token
      try {
        const hasSession = await sessionCache.hasSession();

        if (hasSession) {
          const newToken = await tokenCache.getToken(() => sessionCache.hasSession());

          if (newToken && error.config) {
            // Retry original request with new token
            error.config.headers.Authorization = `Bearer ${newToken}`;
            return apiClient(error.config);
          }
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
      }

      // Sign out and redirect
      await signOut();
      window.location.href = '/login?session_expired=true';
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

## Usage Examples

### Basic API Calls

```ts
import apiClient from '@/lib/api-client';

// GET request
async function getTasks(userId: string) {
  try {
    const response = await apiClient.get(`/v1/${userId}/tasks`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch tasks:', error);
    throw error;
  }
}

// POST request
async function createTask(userId: string, taskData: any) {
  try {
    const response = await apiClient.post(`/v1/${userId}/tasks`, taskData);
    return response.data;
  } catch (error) {
    console.error('Failed to create task:', error);
    throw error;
  }
}

// PUT request
async function updateTask(userId: string, taskId: number, taskData: any) {
  try {
    const response = await apiClient.put(`/v1/${userId}/tasks/${taskId}`, taskData);
    return response.data;
  } catch (error) {
    console.error('Failed to update task:', error);
    throw error;
  }
}

// DELETE request
async function deleteTask(userId: string, taskId: number) {
  try {
    await apiClient.delete(`/v1/${userId}/tasks/${taskId}`);
  } catch (error) {
    console.error('Failed to delete task:', error);
    throw error;
  }
}
```

### React Hook Integration

```tsx
// hooks/useTasks.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuthContext } from '@/contexts/AuthContext';
import apiClient from '@/lib/api-client';

export function useTasks() {
  const { user } = useAuthContext();
  const queryClient = useQueryClient();

  // Fetch tasks
  const { data: tasks, isLoading, error } = useQuery({
    queryKey: ['tasks', user?.id],
    queryFn: async () => {
      if (!user) return [];
      const response = await apiClient.get(`/v1/${user.id}/tasks`);
      return response.data.tasks;
    },
    enabled: !!user,
  });

  // Create task mutation
  const createTask = useMutation({
    mutationFn: async (taskData: any) => {
      if (!user) throw new Error('Not authenticated');
      const response = await apiClient.post(`/v1/${user.id}/tasks`, taskData);
      return response.data.task;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', user?.id] });
    },
  });

  // Update task mutation
  const updateTask = useMutation({
    mutationFn: async ({ taskId, data }: { taskId: number; data: any }) => {
      if (!user) throw new Error('Not authenticated');
      const response = await apiClient.put(`/v1/${user.id}/tasks/${taskId}`, data);
      return response.data.task;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', user?.id] });
    },
  });

  // Delete task mutation
  const deleteTask = useMutation({
    mutationFn: async (taskId: number) => {
      if (!user) throw new Error('Not authenticated');
      await apiClient.delete(`/v1/${user.id}/tasks/${taskId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', user?.id] });
    },
  });

  return {
    tasks,
    isLoading,
    error,
    createTask,
    updateTask,
    deleteTask,
  };
}
```

### Component Usage

```tsx
// components/TaskList.tsx
'use client';

import { useTasks } from '@/hooks/useTasks';

export function TaskList() {
  const { tasks, isLoading, error, createTask, deleteTask } = useTasks();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading tasks</div>;

  const handleCreate = async () => {
    await createTask.mutateAsync({
      title: 'New Task',
      description: 'Task description',
    });
  };

  const handleDelete = async (taskId: number) => {
    await deleteTask.mutateAsync(taskId);
  };

  return (
    <div>
      <button onClick={handleCreate}>Add Task</button>
      <ul>
        {tasks?.map((task) => (
          <li key={task.id}>
            {task.title}
            <button onClick={() => handleDelete(task.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## Error Handling

### Custom Error Handler

```ts
// lib/api-error-handler.ts
import { AxiosError } from 'axios';

export function handleApiError(error: unknown) {
  if (error instanceof AxiosError) {
    if (error.response) {
      // Server responded with error
      const status = error.response.status;
      const message = error.response.data?.detail || 'An error occurred';

      switch (status) {
        case 400:
          return { error: 'Invalid request', message };
        case 401:
          return { error: 'Unauthorized', message: 'Please sign in' };
        case 403:
          return { error: 'Forbidden', message: 'Access denied' };
        case 404:
          return { error: 'Not found', message };
        case 422:
          return { error: 'Validation error', message };
        case 500:
          return { error: 'Server error', message: 'Please try again later' };
        default:
          return { error: 'Error', message };
      }
    } else if (error.request) {
      // Request made but no response
      return { error: 'Network error', message: 'No response from server' };
    }
  }

  return { error: 'Unknown error', message: 'An unexpected error occurred' };
}
```

## Performance Optimization

### Token Caching Benefits

- **Reduces API calls**: Token fetched once per 27 minutes (30min - 3min buffer)
- **Prevents duplicates**: Promise chaining prevents concurrent fetches
- **Memory efficient**: Single token stored, no localStorage overhead

### Session Caching Benefits

- **Reduces overhead**: Session checked once per 60 seconds
- **Faster requests**: Immediate availability for subsequent calls
- **Better UX**: No delay for session validation

## Security Considerations

1. **No localStorage**: Tokens stored in memory only (prevents XSS)
2. **Automatic cleanup**: Tokens cleared on sign out
3. **Session validation**: Always verify session before token generation
4. **HTTPS only**: Enforce secure transmission in production

## Troubleshooting

### Token Not Attached

**Symptoms**: 401 errors despite being logged in

**Solutions**:
1. Verify Better Auth session exists
2. Check token endpoint returns valid JWT
3. Ensure `BETTER_AUTH_SECRET` matches backend
4. Check browser console for errors

### Infinite Refresh Loop

**Symptoms**: Continuous token fetch requests

**Solutions**:
1. Verify token expiry buffer calculation
2. Check `fetchPromise` is cleared after fetch
3. Ensure session cache TTL is reasonable
4. Validate token structure includes `exp` claim

### CORS Errors

**Symptoms**: Preflight request failures

**Solutions**:
1. Add frontend URL to backend CORS config
2. Ensure `withCredentials: true` in axios config
3. Verify backend allows credentials
4. Check `Access-Control-Allow-Origin` header

## Next Steps

- Review JWT token flow (see `jwt-token-flow.md`)
- Implement FastAPI validation (see `fastapi-integration.md`)
- Set up security best practices (see `security-patterns.md`)
