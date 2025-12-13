import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
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

  // Debounce search term to avoid excessive API calls
  const debouncedSearchTerm = useDebouncedValue(searchTerm, 300);

  // Fetch tasks with React Query (automatic caching, deduplication, background refetching)
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['tasks', user?.id, debouncedSearchTerm],
    queryFn: async () => {
      if (!user?.id) return { items: [] };
      const response = await apiClient.get<{ items: Task[] }>(`/v1/${user.id}/tasks`, {
        params: { q: debouncedSearchTerm || undefined },
      });
      return response.data;
    },
    enabled: !!user?.id && !authLoading, // Only fetch when user is available
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const tasks = data?.items || [];

  // Update task status mutation with optimistic updates
  const updateStatusMutation = useMutation({
    mutationFn: async ({ taskId, status }: { taskId: number; status: string }) => {
      if (!user?.id) throw new Error('User not authenticated');
      const response = await apiClient.patch<Task>(`/v1/${user.id}/tasks/${taskId}`, { status });
      return response.data;
    },
    onMutate: async ({ taskId, status }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['tasks', user?.id] });

      // Snapshot previous value
      const previousTasks = queryClient.getQueryData(['tasks', user?.id, debouncedSearchTerm]);

      // Optimistically update
      queryClient.setQueryData(['tasks', user?.id, debouncedSearchTerm], (old: any) => {
        if (!old?.items) return old;
        return {
          ...old,
          items: old.items.map((task: Task) =>
            task.id === taskId ? { ...task, status, completed: status === 'completed' } : task
          ),
        };
      });

      return { previousTasks };
    },
    onSuccess: (data, variables) => {
      toast.success(`Task status updated to ${variables.status}`);
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
      // Refetch after mutation
      queryClient.invalidateQueries({ queryKey: ['tasks', user?.id] });
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
            task.id === taskId ? { ...task, ...taskData } : task
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
      queryClient.invalidateQueries({ queryKey: ['tasks', user?.id] });
    },
  });

  // Delete task mutation with optimistic updates
  const deleteTaskMutation = useMutation({
    mutationFn: async (taskId: number) => {
      if (!user?.id) throw new Error('User not authenticated');
      await apiClient.delete(`/v1/${user.id}/tasks/${taskId}`);
      return taskId;
    },
    onMutate: async (taskId) => {
      await queryClient.cancelQueries({ queryKey: ['tasks', user?.id] });
      const previousTasks = queryClient.getQueryData(['tasks', user?.id, debouncedSearchTerm]);

      queryClient.setQueryData(['tasks', user?.id, debouncedSearchTerm], (old: any) => {
        if (!old?.items) return old;
        return {
          ...old,
          items: old.items.filter((task: Task) => task.id !== taskId),
        };
      });

      return { previousTasks };
    },
    onSuccess: () => {
      toast.success('Task deleted successfully');
    },
    onError: (err, variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(['tasks', user?.id, debouncedSearchTerm], context.previousTasks);
      }
      console.error('Failed to delete task:', err);
      toast.error('Failed to delete task');
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', user?.id] });
    },
  });

  return {
    tasks,
    isLoadingTasks: isLoading,
    isCreatingTask: createTaskMutation.isPending,
    isUpdatingTask: updateTaskMutation.isPending,
    isDeletingTask: deleteTaskMutation.isPending,
    updateTaskStatus: (taskId: number, status: string) => updateStatusMutation.mutate({ taskId, status }),
    updateTask: (taskId: number, taskData: Partial<Task>) => updateTaskMutation.mutate({ taskId, taskData }),
    createTask: (taskData: {
      title: string;
      description: string;
      priority: string;
      status: string;
      dueDate: string;
      recurrenceRule?: string | null;
    }) => createTaskMutation.mutate(taskData),
    deleteTask: (taskId: number) => deleteTaskMutation.mutate(taskId),
    refetch,
  };
}
