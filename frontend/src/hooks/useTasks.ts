import { useEffect, useCallback } from 'react';
import apiClient from '@/lib/api-client';
import { useUIStore } from '@/store/ui-store';
import { Task } from '@/types';

type TaskDisplay = Task & {
  ui_status: 'Not Started' | 'In Progress' | 'Completed';
  is_loading: boolean;
};

export function useTasks() {
  const { tasks, isLoadingTasks, setIsLoadingTasks, setTasks, setError, searchTerm } = useUIStore();

  const fetchTasks = useCallback(async () => {
    setIsLoadingTasks(true);
    try {
      const response = await apiClient.get<Task[]>('/tasks', {
        params: { q: searchTerm || undefined },
      });
      const tasksWithUiProps: TaskDisplay[] = response.data.map(task => ({
        ...task,
        ui_status: task.completed ? 'Completed' : 'Not Started',
        is_loading: false,
      }));
      setTasks(tasksWithUiProps);
    } catch (err) {
      setError('Failed to fetch tasks.');
      console.error(err);
    } finally {
      setIsLoadingTasks(false);
    }
  }, [setTasks, setIsLoadingTasks, setError, searchTerm]); // Add searchTerm to dependencies

  useEffect(() => {
    const handler = setTimeout(() => {
      fetchTasks();
    }, 500); // Debounce for 500ms

    return () => {
      clearTimeout(handler);
    };
  }, [fetchTasks, searchTerm]); // Trigger fetch when searchTerm changes (debounced)

  const updateTaskStatus = async (taskId: number, completed: boolean) => {
    const originalTasks = tasks;
    // Optimistic update
    setTasks(
      tasks.map((task) =>
        task.id === taskId ? { ...task, completed, is_loading: true } : task
      )
    );

    try {
      const response = await apiClient.patch<Task>(`/tasks/${taskId}`, { completed });
      setTasks(
        tasks.map((task) =>
          task.id === taskId
            ? { ...task, ...response.data, ui_status: response.data.completed ? 'Completed' : 'Not Started', is_loading: false }
            : task
        )
      );
    } catch (err) {
      setError('Failed to update task status.');
      console.error(err);
      // Revert optimistic update
      setTasks(originalTasks);
    }
  };

  const createTask = async (taskData: { title: string; description: string; priority: 'low' | 'medium' | 'high'; dueDate: string }) => {
    try {
      const response = await apiClient.post<Task>('/tasks', {
        ...taskData,
        due_date: taskData.dueDate || null,
      });
      const newTaskWithUiProps: TaskDisplay = {
        ...response.data,
        ui_status: 'Not Started',
        is_loading: false,
      };
      setTasks([...tasks, newTaskWithUiProps]);
    } catch (err) {
      setError('Failed to create task.');
      console.error(err);
    }
  };

  return { tasks, isLoadingTasks, updateTaskStatus, createTask };
}
