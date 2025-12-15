import { useEffect, useState, useCallback } from 'react';
import {
  isOnline,
  addOnlineListener,
  getPendingChangesCount,
  queueTaskCreation,
  queueTaskUpdate,
  cacheTasks,
  getCachedTasks,
  registerServiceWorker,
} from '@/lib/offline';

interface UseOfflineReturn {
  isOnline: boolean;
  pendingCount: number;
  queueTask: (taskData: unknown) => Promise<void>;
  queueUpdate: (taskId: number, updateData: unknown) => Promise<void>;
  cacheTaskList: (tasks: unknown[]) => Promise<void>;
  getCachedTaskList: () => Promise<unknown[]>;
}

/**
 * Hook for managing offline functionality
 */
export function useOffline(): UseOfflineReturn {
  const [online, setOnline] = useState(true);
  const [pendingCount, setPendingCount] = useState(0);

  // Initialize service worker and offline state
  useEffect(() => {
    // Register service worker
    registerServiceWorker().catch(console.error);

    // Set initial online status
    setOnline(isOnline());

    // Get initial pending changes count
    getPendingChangesCount().then(setPendingCount).catch(console.error);

    // Listen for online/offline events
    const removeListener = addOnlineListener((status) => {
      setOnline(status);

      if (status) {
        // When coming back online, update pending count
        getPendingChangesCount().then(setPendingCount).catch(console.error);
      }
    });

    return removeListener;
  }, []);

  // Queue a task creation for offline sync
  const queueTask = useCallback(async (taskData: unknown) => {
    await queueTaskCreation(taskData);
    const count = await getPendingChangesCount();
    setPendingCount(count);
  }, []);

  // Queue a task update for offline sync
  const queueUpdate = useCallback(async (taskId: number, updateData: unknown) => {
    await queueTaskUpdate(taskId, updateData);
    const count = await getPendingChangesCount();
    setPendingCount(count);
  }, []);

  // Cache task list for offline access
  const cacheTaskList = useCallback(async (tasks: unknown[]) => {
    await cacheTasks(tasks);
  }, []);

  // Get cached task list
  const getCachedTaskList = useCallback(async () => {
    return await getCachedTasks();
  }, []);

  return {
    isOnline: online,
    pendingCount,
    queueTask,
    queueUpdate,
    cacheTaskList,
    getCachedTaskList,
  };
}
