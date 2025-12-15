"use client";

import { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { useTasks } from '@/hooks/useTasks';
import { useTags } from '@/hooks/useTags';
import { useAuth } from '@/hooks/useAuth';
import TaskCard from '@/components/tasks/TaskCard';
import { DraggableTaskList } from '@/components/tasks/DraggableTaskList';
import TaskStatusChart from '@/components/dashboard/TaskStatusChart';
import CompletedTaskList from '@/components/tasks/CompletedTaskList';
import { TaskListSkeleton } from '@/components/tasks/TaskSkeleton';
import withAuth from '@/components/withAuth';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { toast } from 'sonner';
import { Plus, UserPlus, Keyboard } from 'lucide-react';
import { Task } from '@/types';
import { useKeyboardShortcuts, getTaskManagementShortcuts } from '@/hooks/useKeyboardShortcuts';
import { KeyboardShortcutsHelp } from '@/components/KeyboardShortcutsHelp';
import { OfflineIndicator } from '@/components/OfflineIndicator';
import { useOffline } from '@/hooks/useOffline';

// Code-split modals for better initial page load performance
const CreateTaskModal = dynamic(() => import('@/components/tasks/CreateTaskModal'), {
  loading: () => null, // No loading state needed for modals
});

const EditTaskModal = dynamic(() => import('@/components/tasks/EditTaskModal'), {
  loading: () => null,
});

function DashboardPage() {
  const {
    tasks,
    isLoadingTasks,
    isCreatingTask,
    isUpdatingTask,
    isDeletingTask,
    updateTaskStatus,
    updateTask,
    createTask,
    deleteTask,
    reorderTasks,
    refetch,
    isTaskUpdating,
    isTaskDeleting,
  } = useTasks();
  const { associateTagWithTask, dissociateTagFromTask } = useTags();
  const { user } = useAuth();
  const { isOnline, cacheTaskList } = useOffline();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isShortcutsHelpOpen, setIsShortcutsHelpOpen] = useState(false);
  const [selectedTaskIndex, setSelectedTaskIndex] = useState<number>(0);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Cache tasks for offline access whenever they change
  useEffect(() => {
    if (tasks.length > 0) {
      cacheTaskList(tasks).catch(console.error);
    }
  }, [tasks, cacheTaskList]);

  // Extract first name from user name or use email
  const getFirstName = (name: string | null, email: string) => {
    if (name && name.trim()) {
      // Get first word of name
      return name.trim().split(' ')[0];
    }
    // Fallback to email username (part before @)
    return email.split('@')[0];
  };

  const firstName = user ? getFirstName(user.name, user.email) : "User";

  // Mock team members
  const teamMembers = [
    { id: '1', name: 'Alice Johnson', avatar: '', initials: 'AJ' },
    { id: '2', name: 'Bob Smith', avatar: '', initials: 'BS' },
    { id: '3', name: 'Carol White', avatar: '', initials: 'CW' },
  ];

  const handleCreateTask = useCallback(async (taskData: { title: string; description: string; priority: string; status: string; dueDate: string }) => {
    try {
      await createTask(taskData);
      setIsCreateModalOpen(false);
    } catch (error) {
      // Error is already handled by the mutation's onError
      // Just keep the modal open so user can retry
      console.error('Failed to create task:', error);
    }
  }, [createTask]);

  const handleEditTask = useCallback((task: Task) => {
    setEditingTask(task);
  }, []);

  const handleUpdateTask = useCallback(async (taskData: { title: string; description: string; priority: string; dueDate: string; tagIds: number[] }) => {
    if (editingTask) {
      try {
        // Update task properties
        await updateTask(editingTask.id, {
          title: taskData.title,
          description: taskData.description,
          priority: taskData.priority,
          due_date: taskData.dueDate || null,
        });

        // Close modal immediately after the main update completes
        setEditingTask(null);

        // Handle tag changes in the background after closing the modal
        const currentTagIds = editingTask.tags?.map(tag => tag.id) || [];
        const newTagIds = taskData.tagIds;

        // Find tags to add and remove
        const tagsToAdd = newTagIds.filter(id => !currentTagIds.includes(id));
        const tagsToRemove = currentTagIds.filter(id => !newTagIds.includes(id));

        // Process tag operations in the background without waiting for them
        if (tagsToAdd.length > 0 || tagsToRemove.length > 0) {
          // Create a separate promise that runs in the background
          const processTagChanges = async () => {
            // Batch tag operations - run all API calls in parallel for much better performance
            const tagOperations = [
              ...tagsToAdd.map(tagId =>
                associateTagWithTask(editingTask.id, tagId).catch(err => {
                  console.error('Failed to associate tag:', err);
                })
              ),
              ...tagsToRemove.map(tagId =>
                dissociateTagFromTask(editingTask.id, tagId).catch(err => {
                  console.error('Failed to dissociate tag:', err);
                })
              ),
            ];

            // Wait for all tag operations to complete in parallel
            await Promise.all(tagOperations);

            // Refetch tasks to get updated tag associations
            await refetch();
          };

          // Execute the tag operations in the background without awaiting
          processTagChanges().catch(console.error);
        }
      } catch (error) {
        // Error is already handled by the mutation's onError
        // Just keep the modal open so user can retry
        console.error('Failed to update task:', error);
      }
    }
  }, [editingTask, updateTask, associateTagWithTask, dissociateTagFromTask, refetch]);

  const handleDeleteTask = useCallback(async (taskId: number) => {
    try {
      await deleteTask(taskId);
      toast.success('Task deleted');
    } catch (error) {
      // Error toast is already shown by the mutation
      console.error('Delete failed:', error);
    }
  }, [deleteTask]);

  const handleRestoreTask = useCallback(async (taskId: number) => {
    await updateTaskStatus(taskId, 'not_started');
  }, [updateTaskStatus]);

  const pendingTasks = useMemo(() => tasks.filter(t => t.status !== 'completed'), [tasks]);

  const currentDate = useMemo(() => new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric'
  }), []);

  // Keyboard shortcuts handlers
  const handleSearch = useCallback(() => {
    searchInputRef.current?.focus();
  }, []);

  const handleNewTask = useCallback(() => {
    setIsCreateModalOpen(true);
  }, []);

  const handleCompleteTask = useCallback(() => {
    if (pendingTasks.length > 0 && selectedTaskIndex < pendingTasks.length) {
      const task = pendingTasks[selectedTaskIndex];
      const newStatus = task.status === 'completed' ? 'not_started' : 'completed';
      updateTaskStatus(task.id, newStatus);
    }
  }, [pendingTasks, selectedTaskIndex, updateTaskStatus]);

  const handleDeleteSelectedTask = useCallback(() => {
    if (pendingTasks.length > 0 && selectedTaskIndex < pendingTasks.length) {
      const task = pendingTasks[selectedTaskIndex];
      handleDeleteTask(task.id);
    }
  }, [pendingTasks, selectedTaskIndex, handleDeleteTask]);

  const handleCloseModal = useCallback(() => {
    if (isCreateModalOpen) {
      setIsCreateModalOpen(false);
    } else if (editingTask) {
      setEditingTask(null);
    } else if (isShortcutsHelpOpen) {
      setIsShortcutsHelpOpen(false);
    }
  }, [isCreateModalOpen, editingTask, isShortcutsHelpOpen]);

  const handleShowHelp = useCallback(() => {
    setIsShortcutsHelpOpen(!isShortcutsHelpOpen);
  }, [isShortcutsHelpOpen]);

  // Register keyboard shortcuts
  const shortcuts = useMemo(
    () =>
      getTaskManagementShortcuts({
        onSearch: handleSearch,
        onNewTask: handleNewTask,
        onComplete: handleCompleteTask,
        onClose: handleCloseModal,
        onDelete: handleDeleteSelectedTask,
        onHelp: handleShowHelp,
      }),
    [handleSearch, handleNewTask, handleCompleteTask, handleCloseModal, handleDeleteSelectedTask, handleShowHelp]
  );

  useKeyboardShortcuts(shortcuts);

  return (
    <div className="p-4 md:p-6 space-y-4 md:space-y-6">
      {/* Welcome Section */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl md:text-2xl font-bold text-gray-900 mb-1">
            Welcome back, {firstName}! 👋
          </h1>
          <p className="text-xs md:text-sm text-gray-600">Here&apos;s what&apos;s happening with your tasks today.</p>
        </div>

        {/* Team Members */}
        <div className="flex items-center gap-3">
          <div className="flex -space-x-2">
            {teamMembers.map((member) => (
              <Avatar key={member.id} className="h-7 w-7 md:h-8 md:w-8 border-2 border-white">
                <AvatarImage src={member.avatar} alt={member.name} />
                <AvatarFallback className="bg-coral text-white text-xs">{member.initials}</AvatarFallback>
              </Avatar>
            ))}
          </div>
          <Button variant="outline" size="sm" className="gap-2 text-xs md:text-sm">
            <UserPlus className="h-3 w-3 md:h-4 md:w-4" />
            <span className="hidden sm:inline">Invite</span>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsShortcutsHelpOpen(true)}
            className="gap-2 text-xs md:text-sm"
            aria-label="Show keyboard shortcuts"
          >
            <Keyboard className="h-3 w-3 md:h-4 md:w-4" />
            <span className="hidden sm:inline">Shortcuts</span>
          </Button>
        </div>
      </div>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
        {/* Left Panel - To-Do Section */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 md:p-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-3">
              <div>
                <h2 className="text-base md:text-lg font-semibold text-gray-900">To-Do</h2>
                <p className="text-xs md:text-sm text-gray-600">{currentDate} · Today</p>
              </div>
              <Button
                onClick={() => setIsCreateModalOpen(true)}
                className="gap-2 bg-coral hover:bg-coral-600 w-full sm:w-auto text-sm"
                aria-label="Create new task (Ctrl+N or Cmd+N)"
              >
                <Plus className="h-4 w-4" />
                Add Task
              </Button>
            </div>

            {/* Task List */}
            <div className="space-y-3">
              {isLoadingTasks ? (
                <TaskListSkeleton count={3} />
              ) : pendingTasks.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <p className="mb-2">No tasks yet</p>
                  <p className="text-sm">Click &quot;Add Task&quot; to create your first task</p>
                </div>
              ) : (
                <DraggableTaskList
                  tasks={pendingTasks}
                  onToggleComplete={updateTaskStatus}
                  onEdit={handleEditTask}
                  onDelete={handleDeleteTask}
                  onReorder={reorderTasks}
                  isUpdating={isUpdatingTask}
                  isDeleting={isDeletingTask}
                  isTaskUpdating={isTaskUpdating}
                  isTaskDeleting={isTaskDeleting}
                />
              )}
            </div>
          </div>
        </div>

        {/* Right Panel */}
        <div className="space-y-4 md:space-y-6">
          {/* Task Status Chart */}
          <TaskStatusChart tasks={tasks} />

          {/* Completed Tasks Section */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 md:p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="h-6 md:h-8 w-1 bg-coral rounded" />
              <h2 className="text-base md:text-lg font-semibold text-gray-900">Completed Task</h2>
            </div>
            <CompletedTaskList
              tasks={tasks}
              onRestore={handleRestoreTask}
              onDelete={handleDeleteTask}
              isUpdating={isUpdatingTask}
              isDeleting={isDeletingTask}
              isTaskUpdating={isTaskUpdating}
              isTaskDeleting={isTaskDeleting}
            />
          </div>
        </div>
      </div>

      {/* Create Task Modal */}
      <CreateTaskModal
        isOpen={isCreateModalOpen}
        onOpenChange={setIsCreateModalOpen}
        onSubmit={handleCreateTask}
        isLoading={isCreatingTask}
      />

      {/* Edit Task Modal */}
      <EditTaskModal
        task={editingTask}
        isOpen={!!editingTask}
        onOpenChange={(open) => !open && setEditingTask(null)}
        onSubmit={handleUpdateTask}
        isLoading={isUpdatingTask}
      />

      {/* Keyboard Shortcuts Help */}
      <KeyboardShortcutsHelp
        isOpen={isShortcutsHelpOpen}
        onClose={() => setIsShortcutsHelpOpen(false)}
        shortcuts={shortcuts}
      />

      {/* Offline Indicator */}
      <OfflineIndicator />
    </div>
  );
}

export default withAuth(DashboardPage);
