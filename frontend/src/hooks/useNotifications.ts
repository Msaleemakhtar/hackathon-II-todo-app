import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';
import { useAuth } from '@/hooks/useAuth';
import { toast } from 'sonner';

interface Reminder {
  id: number;
  task_id: number;
  user_id: string;
  remind_at: string;
  channel: 'browser' | 'email' | 'both';
  is_sent: boolean;
  sent_at?: string | null;
  message?: string | null;
  snoozed_until?: string | null;
  created_at: string;
  updated_at: string;
}

interface ReminderCreate {
  task_id: number;
  remind_at: string;
  channel: 'browser' | 'email' | 'both';
  message?: string;
}

interface ReminderUpdate {
  remind_at?: string;
  channel?: 'browser' | 'email' | 'both';
  message?: string;
  snoozed_until?: string;
}

export function useNotifications() {
  const { user, loading: authLoading } = useAuth();
  const queryClient = useQueryClient();

  // Fetch reminders with React Query
  const { data: reminders = [], isLoading, error, refetch } = useQuery({
    queryKey: ['reminders', user?.id],
    queryFn: async () => {
      if (!user?.id) return [];
      const response = await apiClient.get<Reminder[]>(`/v1/${user.id}/reminders`, {
        params: { upcoming_only: true },
      });
      return response.data;
    },
    enabled: !!user?.id && !authLoading,
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes to catch new reminders
  });

  // Count of upcoming reminders
  const upcomingCount = reminders.filter((r) => !r.is_sent).length;

  // Create reminder mutation
  const createReminderMutation = useMutation({
    mutationFn: async (data: ReminderCreate) => {
      if (!user?.id) throw new Error('User not authenticated');
      const response = await apiClient.post<Reminder>(
        `/v1/${user.id}/reminders`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      toast.success('Reminder set successfully');
      queryClient.invalidateQueries({ queryKey: ['reminders', user?.id] });
    },
    onError: (err: any) => {
      console.error('Failed to create reminder:', err);
      toast.error(err.response?.data?.detail || 'Failed to create reminder');
    },
  });

  // Update reminder mutation
  const updateReminderMutation = useMutation({
    mutationFn: async ({ id, data }: { id: number; data: ReminderUpdate }) => {
      if (!user?.id) throw new Error('User not authenticated');
      const response = await apiClient.put<Reminder>(
        `/v1/${user.id}/reminders/${id}`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      toast.success('Reminder updated successfully');
      queryClient.invalidateQueries({ queryKey: ['reminders', user?.id] });
    },
    onError: (err: any) => {
      console.error('Failed to update reminder:', err);
      toast.error(err.response?.data?.detail || 'Failed to update reminder');
    },
  });

  // Delete reminder mutation
  const deleteReminderMutation = useMutation({
    mutationFn: async (id: number) => {
      if (!user?.id) throw new Error('User not authenticated');
      await apiClient.delete(`/v1/${user.id}/reminders/${id}`);
    },
    onMutate: async (id) => {
      // Optimistically update
      await queryClient.cancelQueries({ queryKey: ['reminders', user?.id] });
      const previousReminders = queryClient.getQueryData(['reminders', user?.id]);

      queryClient.setQueryData(['reminders', user?.id], (old: Reminder[] = []) => {
        return old.filter((reminder) => reminder.id !== id);
      });

      return { previousReminders };
    },
    onSuccess: () => {
      toast.success('Reminder cancelled');
    },
    onError: (err: any, id, context) => {
      // Revert optimistic update on error
      if (context?.previousReminders) {
        queryClient.setQueryData(['reminders', user?.id], context.previousReminders);
      }
      console.error('Failed to delete reminder:', err);
      toast.error(err.response?.data?.detail || 'Failed to cancel reminder');
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['reminders', user?.id] });
    },
  });

  // Snooze reminder mutation
  const snoozeReminderMutation = useMutation({
    mutationFn: async ({ id, minutes = 15 }: { id: number; minutes?: number }) => {
      if (!user?.id) throw new Error('User not authenticated');
      const response = await apiClient.post<Reminder>(
        `/v1/${user.id}/reminders/${id}/snooze`,
        null,
        { params: { minutes } }
      );
      return response.data;
    },
    onSuccess: (data, variables) => {
      toast.success(`Reminder snoozed for ${variables.minutes || 15} minutes`);
      queryClient.invalidateQueries({ queryKey: ['reminders', user?.id] });
    },
    onError: (err: any) => {
      console.error('Failed to snooze reminder:', err);
      toast.error(err.response?.data?.detail || 'Failed to snooze reminder');
    },
  });

  return {
    reminders,
    upcomingCount,
    isLoading,
    error,
    refetch,
    createReminder: createReminderMutation.mutate,
    updateReminder: updateReminderMutation.mutate,
    deleteReminder: deleteReminderMutation.mutate,
    snoozeReminder: snoozeReminderMutation.mutate,
    isCreating: createReminderMutation.isPending,
    isUpdating: updateReminderMutation.isPending,
    isDeleting: deleteReminderMutation.isPending,
    isSnoozing: snoozeReminderMutation.isPending,
  };
}
