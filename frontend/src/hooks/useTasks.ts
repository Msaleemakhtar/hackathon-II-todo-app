import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useCallback } from 'react';
import apiClient from '@/lib/api-client';
import { useUIStore } from '@/store/ui-store';
import { useAuth } from '@/hooks/useAuth';
import { useDebouncedValue } from '@/hooks/useDebouncedValue';
import { Task } from '@/types';
import { toast } from 'sonner';

export function useTasks() {
  const { searchTerm } = useUIStore();
  const { user, loading: authLoading } = useAuth();
  const queryClient = useQueryClient();

  // Track which specific task is being operated on for per-task loading states
  const [operatingTaskId, setOperatingTaskId] = useState<number | null>(null);
  const [operationType, setOperationType] = useState<'update' | 'delete' | null>(null);

  // Debounce search term to avoid excessive API calls
  const debouncedSearchTerm = useDebouncedValue(searchTerm, 300);

  // Fetch tasks with React Query (automatic caching, deduplication, background refetching)
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['tasks', user?.id, debouncedSearchTerm],
    queryFn: async () => {
      if (!user?.id) return { items: [] };
      console.log('[Tasks] Fetching tasks for user:', user.id, 'search:', debouncedSearchTerm);
      const response = await apiClient.get<{ items: Task[] }>(`/v1/${user.id}/tasks`, {
        params: { q: debouncedSearchTerm || undefined },
      });
      console.log('[Tasks] Received', response.data.items?.length, 'tasks');
      return response.data;
    },
    enabled: !!user?.id && !authLoading, // Only fetch when user is available
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    refetchOnReconnect: false,
    refetchInterval: false,
  });

  const tasks = data?.items || [];

  // Update task status mutation with optimistic updates
  const updateStatusMutation = useMutation({
    mutationFn: async ({ taskId, status }: { taskId: number; status: string }) => {
      if (!user?.id) throw new Error('User not authenticated');
      // Set operating task for per-task loading state
      setOperatingTaskId(taskId);
      setOperationType('update');
      const response = await apiClient.patch<Task>(`/v1/${user.id}/tasks/${taskId}`, { status });
      return response.data;
    },
    onMutate: async ({ taskId, status }) => {
      // Cancel outgoing refetches to avoid race conditions
      await queryClient.cancelQueries({ queryKey: ['tasks', user?.id] });

      // Snapshot previous value
      const previousTasks = queryClient.getQueryData(['tasks', user?.id, debouncedSearchTerm]);

      // Optimistically update
      queryClient.setQueryData(['tasks', user?.id, debouncedSearchTerm], (old: any) => {
        if (!old?.items) return old;
        return {
          ...old,
          items: old.items.map((task: Task) =>
            task.id === taskId ? { ...task, status, completed: status === 'completed', updated_at: new Date().toISOString() } : task
          ),
        };
      });

      return { previousTasks };
    },
    onSuccess: (data, variables) => {
      const statusLabel = variables.status === 'completed' ? 'completed' :
                          variables.status === 'in_progress' ? 'in progress' :
                          variables.status === 'not_started' ? 'not started' : variables.status;
      toast.success(`Task marked as ${statusLabel}`);
    },
    onError: (err, variables, context) => {
      // Revert optimistic update on error
      if (context?.previousTasks) {
        queryClient.setQueryData(['tasks', user?.id, debouncedSearchTerm], context.previousTasks);
      }
      console.error('Failed to update task status:', err);
      toast.error('Failed to update task status');
    },
    onSettled: () => {
      // Clear operating state
      setOperatingTaskId(null);
      setOperationType(null);
      // NOTE: We don't invalidate queries here to prevent race conditions.
      // The optimistic update with updated_at timestamp is sufficient.
    },
  });

  // Create task mutation
  const createTaskMutation = useMutation({
    mutationFn: async (taskData: {
      title: string;
      description: string;
      priority: string;
      status: string;
      dueDate: string;
      recurrenceRule?: string | null;
    }) => {
      if (!user?.id) throw new Error('User not authenticated');
      const payload = {
        title: taskData.title,
        description: taskData.description || '',
        priority: taskData.priority.toLowerCase(),
        status: taskData.status || 'not_started',
        due_date: taskData.dueDate ? new Date(taskData.dueDate).toISOString() : null,
        recurrence_rule: taskData.recurrenceRule || null,
      };
      const response = await apiClient.post<Task>(`/v1/${user.id}/tasks`, payload);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', user?.id] });
      toast.success('Task created successfully');
    },
    onError: (err: any) => {
      console.error('Task creation failed:', err);
      console.error('Error response:', err.response?.data);
      toast.error('Failed to create task');
    },
  });

  // Update task mutation with optimistic updates
  const updateTaskMutation = useMutation({
    mutationFn: async ({ taskId, taskData }: { taskId: number; taskData: Partial<Task> }) => {
      if (!user?.id) throw new Error('User not authenticated');
      // Set operating task for per-task loading state
      setOperatingTaskId(taskId);
      setOperationType('update');
      const response = await apiClient.patch<Task>(`/v1/${user.id}/tasks/${taskId}`, taskData);
      return response.data;
    },
    onMutate: async ({ taskId, taskData }) => {
      await queryClient.cancelQueries({ queryKey: ['tasks', user?.id] });
      const previousTasks = queryClient.getQueryData(['tasks', user?.id, debouncedSearchTerm]);

      queryClient.setQueryData(['tasks', user?.id, debouncedSearchTerm], (old: any) => {
        if (!old?.items) return old;
        return {
          ...old,
          items: old.items.map((task: Task) =>
            task.id === taskId ? { ...task, ...taskData, updated_at: new Date().toISOString() } : task
          ),
        };
      });

      return { previousTasks };
    },
    onSuccess: () => {
      toast.success('Task updated successfully');
    },
    onError: (err, variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(['tasks', user?.id, debouncedSearchTerm], context.previousTasks);
      }
      console.error('Failed to update task:', err);
      toast.error('Failed to update task');
    },
    onSettled: () => {
      // Clear operating state
      setOperatingTaskId(null);
      setOperationType(null);
      // NOTE: We don't invalidate queries here to prevent race conditions.
      // The optimistic update is sufficient.
    },
  });

  // Delete task mutation with optimistic updates
  const deleteTaskMutation = useMutation({
    mutationFn: async (taskId: number) => {
      if (!user?.id) throw new Error('User not authenticated');
      // Set operating task for per-task loading state
      setOperatingTaskId(taskId);
      setOperationType('delete');

      console.log('[Delete] Starting delete for task:', taskId);
      console.log('[Delete] User ID:', user.id);

      // Unregister service worker to rule out interference
      if ('serviceWorker' in navigator) {
        const registrations = await navigator.serviceWorker.getRegistrations();
        for (const registration of registrations) {
          console.log('[Delete] Unregistering service worker:', registration.scope);
          await registration.unregister();
        }
      }

      // Use native fetch to bypass axios interceptor issues
      const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
      const fullUrl = `${baseUrl}/v1/${user.id}/tasks/${taskId}`;
      console.log('[Delete] Making request to:', fullUrl);

      // Get auth token first
      let token = '';
      try {
        const tokenRes = await fetch('/api/auth/token', { credentials: 'include' });
        if (tokenRes.ok) {
          const tokenData = await tokenRes.json();
          token = tokenData.token;
          console.log('[Delete] Got auth token');
        }
      } catch (e) {
        console.warn('[Delete] Failed to get token:', e);
      }

      // Make the delete request with native fetch
      console.log('[Delete] Token available:', !!token);
      const response = await fetch(fullUrl, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
        },
        mode: 'cors',
      });

      console.log('[Delete] API response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('[Delete] API error:', errorData);
        throw new Error(errorData.detail || `Delete failed with status ${response.status}`);
      }

      // Clear service worker API cache to prevent stale data
      if ('caches' in window) {
        try {
          const cache = await caches.open('todo-app-api-v1');
          const keys = await cache.keys();
          for (const request of keys) {
            if (request.url.includes('/tasks')) {
              await cache.delete(request);
              console.log('[Delete] Cleared cached request:', request.url);
            }
          }
        } catch (e) {
          console.log('[Delete] Cache clear failed (not critical):', e);
        }
      }

      return taskId;
    },
    onMutate: async (taskId) => {
      console.log('[Delete] onMutate - removing task from cache:', taskId);
      // Cancel any outgoing refetches to avoid race conditions
      await queryClient.cancelQueries({ queryKey: ['tasks', user?.id] });
      const previousTasks = queryClient.getQueryData(['tasks', user?.id, debouncedSearchTerm]);

      // Optimistically remove the task from cache
      queryClient.setQueryData(['tasks', user?.id, debouncedSearchTerm], (old: any) => {
        if (!old?.items) return old;
        return {
          ...old,
          items: old.items.filter((task: Task) => task.id !== taskId),
        };
      });

      return { previousTasks, taskId };
    },
    onSuccess: (taskId) => {
      console.log('[Delete] onSuccess - task deleted successfully:', taskId);
      // Remove from all query cache variations (different search terms)
      queryClient.setQueriesData({ queryKey: ['tasks', user?.id] }, (old: any) => {
        if (!old?.items) return old;
        return {
          ...old,
          items: old.items.filter((task: Task) => task.id !== taskId),
        };
      });
    },
    onError: (err: any, taskId, context) => {
      console.error('[Delete] onError - rolling back. Error:', err);
      console.error('[Delete] Error response:', err.response?.data);
      console.error('[Delete] Error status:', err.response?.status);
      console.error('[Delete] Error message:', err.message);
      // Rollback optimistic update on error
      if (context?.previousTasks) {
        console.log('[Delete] Rolling back to previous tasks');
        queryClient.setQueryData(['tasks', user?.id, debouncedSearchTerm], context.previousTasks);
      }
      toast.error(`Failed to delete task: ${err.response?.data?.detail || err.message}`);
    },
    onSettled: (data, error) => {
      console.log('[Delete] onSettled - error:', error, 'data:', data);
      // Clear operating state
      setOperatingTaskId(null);
      setOperationType(null);
    },
  });

  // Reorder tasks mutation with optimistic updates
  const reorderTasksMutation = useMutation({
    mutationFn: async (taskIds: number[]) => {
      if (!user?.id) throw new Error('User not authenticated');
      const response = await apiClient.post(`/v1/${user.id}/tasks/reorder`, { task_ids: taskIds });
      return response.data;
    },
    onMutate: async (taskIds) => {
      await queryClient.cancelQueries({ queryKey: ['tasks', user?.id] });
      const previousTasks = queryClient.getQueryData(['tasks', user?.id, debouncedSearchTerm]);

      // Optimistically reorder tasks in cache
      queryClient.setQueryData(['tasks', user?.id, debouncedSearchTerm], (old: any) => {
        if (!old?.items) return old;

        // Create a map of tasks by ID for quick lookup
        const taskMap = new Map(old.items.map((task: Task) => [task.id, task]));

        // Reorder based on taskIds array
        const reorderedItems = taskIds
          .map(id => taskMap.get(id))
          .filter(Boolean); // Filter out any undefined values

        return {
          ...old,
          items: reorderedItems,
        };
      });

      return { previousTasks };
    },
    onError: (err, variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(['tasks', user?.id, debouncedSearchTerm], context.previousTasks);
      }
      console.error('Failed to reorder tasks:', err);
      toast.error('Failed to save task order');
    },
    onSettled: () => {
      // Don't invalidate immediately to avoid jarring UI updates
      // The optimistic update should be sufficient
    },
  });

  // Helper to check if a specific task is being operated on
  const isTaskOperating = useCallback((taskId: number) => operatingTaskId === taskId, [operatingTaskId]);
  const isTaskUpdating = useCallback((taskId: number) => operatingTaskId === taskId && operationType === 'update', [operatingTaskId, operationType]);
  const isTaskDeleting = useCallback((taskId: number) => operatingTaskId === taskId && operationType === 'delete', [operatingTaskId, operationType]);

  return {
    tasks,
    isLoadingTasks: isLoading,
    isCreatingTask: createTaskMutation.isPending,
    // Global states (any task being updated/deleted)
    isUpdatingTask: updateTaskMutation.isPending || updateStatusMutation.isPending,
    isDeletingTask: deleteTaskMutation.isPending,
    // Per-task loading state helpers
    operatingTaskId,
    isTaskOperating,
    isTaskUpdating,
    isTaskDeleting,
    updateTaskStatus: async (taskId: number, status: string) => {
      await updateStatusMutation.mutateAsync({ taskId, status });
    },
    updateTask: async (taskId: number, taskData: Partial<Task>) => {
      await updateTaskMutation.mutateAsync({ taskId, taskData });
    },
    createTask: async (taskData: {
      title: string;
      description: string;
      priority: string;
      status: string;
      dueDate: string;
      recurrenceRule?: string | null;
    }) => {
      await createTaskMutation.mutateAsync(taskData);
    },
    deleteTask: async (taskId: number) => {
      await deleteTaskMutation.mutateAsync(taskId);
    },
    reorderTasks: async (taskIds: number[]) => {
      await reorderTasksMutation.mutateAsync(taskIds);
    },
    refetch,
  };
}
