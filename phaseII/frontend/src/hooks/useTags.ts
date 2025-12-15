import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';
import { useAuth } from '@/hooks/useAuth';
import { Tag } from '@/types';
import { toast } from 'sonner';

export function useTags() {
  const { user, loading: authLoading } = useAuth();
  const queryClient = useQueryClient();

  // Fetch tags with React Query (automatic caching)
  const { data, isLoading } = useQuery({
    queryKey: ['tags', user?.id],
    queryFn: async () => {
      if (!user?.id) return [];
      const response = await apiClient.get<Tag[]>(`/v1/${user.id}/tags`);
      return response.data;
    },
    enabled: !!user?.id && !authLoading,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const tags = data || [];

  // Create tag mutation
  const createTagMutation = useMutation({
    mutationFn: async (tagData: { name: string; color?: string }) => {
      if (!user?.id) throw new Error('User not authenticated');
      const response = await apiClient.post<Tag>(`/v1/${user.id}/tags`, tagData);
      return response.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tags', user?.id] });
      toast.success(`Tag "${variables.name}" created successfully`);
    },
    onError: (err, variables) => {
      console.error('Failed to create tag:', err);
      toast.error('Failed to create tag');
    },
  });

  // Update tag mutation
  const updateTagMutation = useMutation({
    mutationFn: async ({ tagId, tagData }: { tagId: number; tagData: { name: string; color?: string } }) => {
      if (!user?.id) throw new Error('User not authenticated');
      const response = await apiClient.put<Tag>(`/v1/${user.id}/tags/${tagId}`, tagData);
      return response.data;
    },
    onMutate: async ({ tagId, tagData }) => {
      await queryClient.cancelQueries({ queryKey: ['tags', user?.id] });
      const previousTags = queryClient.getQueryData(['tags', user?.id]);

      queryClient.setQueryData(['tags', user?.id], (old: Tag[] | undefined) => {
        if (!old) return old;
        return old.map((tag) => (tag.id === tagId ? { ...tag, ...tagData } : tag));
      });

      return { previousTags };
    },
    onSuccess: (data, variables) => {
      toast.success(`Tag "${variables.tagData.name}" updated successfully`);
    },
    onError: (err, variables, context) => {
      if (context?.previousTags) {
        queryClient.setQueryData(['tags', user?.id], context.previousTags);
      }
      console.error('Failed to update tag:', err);
      toast.error('Failed to update tag');
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['tags', user?.id] });
    },
  });

  // Delete tag mutation
  const deleteTagMutation = useMutation({
    mutationFn: async (tagId: number) => {
      if (!user?.id) throw new Error('User not authenticated');
      await apiClient.delete(`/v1/${user.id}/tags/${tagId}`);
      return tagId;
    },
    onMutate: async (tagId) => {
      await queryClient.cancelQueries({ queryKey: ['tags', user?.id] });
      const previousTags = queryClient.getQueryData(['tags', user?.id]);

      queryClient.setQueryData(['tags', user?.id], (old: Tag[] | undefined) => {
        if (!old) return old;
        return old.filter((tag) => tag.id !== tagId);
      });

      return { previousTags };
    },
    onSuccess: () => {
      toast.success('Tag deleted successfully');
    },
    onError: (err, variables, context) => {
      if (context?.previousTags) {
        queryClient.setQueryData(['tags', user?.id], context.previousTags);
      }
      console.error('Failed to delete tag:', err);
      toast.error('Failed to delete tag');
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['tags', user?.id] });
    },
  });

  // Associate tag with task mutation
  const associateTagMutation = useMutation({
    mutationFn: async ({ taskId, tagId }: { taskId: number; tagId: number }) => {
      if (!user?.id) throw new Error('User not authenticated');
      const response = await apiClient.post(`/v1/${user.id}/tasks/${taskId}/tags/${tagId}`);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate tasks query to refresh task data with updated tags
      queryClient.invalidateQueries({ queryKey: ['tasks', user?.id] });
      toast.success('Tag added to task');
    },
    onError: (err) => {
      console.error('Failed to add tag to task:', err);
      toast.error('Failed to add tag to task');
    },
  });

  // Dissociate tag from task mutation
  const dissociateTagMutation = useMutation({
    mutationFn: async ({ taskId, tagId }: { taskId: number; tagId: number }) => {
      if (!user?.id) throw new Error('User not authenticated');
      await apiClient.delete(`/v1/${user.id}/tasks/${taskId}/tags/${tagId}`);
    },
    onSuccess: () => {
      // Invalidate tasks query to refresh task data
      queryClient.invalidateQueries({ queryKey: ['tasks', user?.id] });
      toast.success('Tag removed from task');
    },
    onError: (err) => {
      console.error('Failed to remove tag from task:', err);
      toast.error('Failed to remove tag from task');
    },
  });

  return {
    tags,
    isLoadingTags: isLoading,
    createTag: (tagData: { name: string; color?: string }) => createTagMutation.mutateAsync(tagData),
    updateTag: (tagId: number, tagData: { name: string; color?: string }) =>
      updateTagMutation.mutate({ tagId, tagData }),
    deleteTag: (tagId: number) => deleteTagMutation.mutate(tagId),
    associateTagWithTask: (taskId: number, tagId: number) =>
      associateTagMutation.mutateAsync({ taskId, tagId }),
    dissociateTagFromTask: (taskId: number, tagId: number) =>
      dissociateTagMutation.mutateAsync({ taskId, tagId }),
  };
}
