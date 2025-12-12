"use client";

import { useState, useCallback, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { useTasks } from '@/hooks/useTasks';
import { useTags } from '@/hooks/useTags';
import { useUIStore } from '@/store/ui-store';
import { TaskListSkeleton } from '@/components/tasks/TaskSkeleton';
import withAuth from '@/components/withAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Calendar, Clock, Flag, Search, Plus, Edit } from 'lucide-react';
import { Task } from '@/types';

// Code-split modals for better initial page load performance
const CreateTaskModal = dynamic(() => import('@/components/tasks/CreateTaskModal'), {
  loading: () => null,
});

const EditTaskModal = dynamic(() => import('@/components/tasks/EditTaskModal'), {
  loading: () => null,
});

const TaskDetailModal = dynamic(() => import('@/components/tasks/TaskDetailModal'), {
  loading: () => null,
});

function MyTasksPage() {
  const { tasks, isLoadingTasks, isCreatingTask, isUpdatingTask, isDeletingTask, updateTaskStatus, updateTask, createTask, deleteTask, refetch } = useTasks();
  const { associateTagWithTask, dissociateTagFromTask } = useTags();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [selectedTask, setSelectedTask] = useState<any>(null);
  // Use UI store for search to leverage server-side search and debouncing
  const { searchTerm, setSearchTerm } = useUIStore();

  const handleCreateTask = useCallback(async (taskData: { title: string; description: string; priority: string; status: string; dueDate: string }) => {
    await createTask(taskData);
    setIsCreateModalOpen(false);
  }, [createTask]);

  const handleEditTask = useCallback((task: Task, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingTask(task);
  }, []);

  const handleUpdateTask = useCallback(async (taskData: { title: string; description: string; priority: string; dueDate: string; tagIds: number[] }) => {
    if (editingTask) {
      // Update task properties
      await updateTask(editingTask.id, {
        title: taskData.title,
        description: taskData.description,
        priority: taskData.priority,
        due_date: taskData.dueDate || null,
      });

      // Handle tag changes
      const currentTagIds = editingTask.tags?.map(tag => tag.id) || [];
      const newTagIds = taskData.tagIds;

      // Find tags to add and remove
      const tagsToAdd = newTagIds.filter(id => !currentTagIds.includes(id));
      const tagsToRemove = currentTagIds.filter(id => !newTagIds.includes(id));

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

      setEditingTask(null);
    }
  }, [editingTask, updateTask, associateTagWithTask, dissociateTagFromTask, refetch]);

  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'medium':
        return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'low':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'in_progress':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'not_started':
        return 'bg-gray-100 text-gray-700 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const formatStatus = (status: string) => {
    return status.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  // Server-side search is already handled by useTasks hook via searchTerm
  // No need for client-side filtering - tasks are already filtered

  const handleTaskClick = useCallback((task: any) => {
    setSelectedTask(task);
  }, []);

  const handleCloseModal = useCallback((open: boolean) => {
    if (!open) setSelectedTask(null);
  }, []);

  return (
    <div className="p-4 md:p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-4 md:mb-6">
        <h1 className="text-xl md:text-2xl font-bold text-gray-900 mb-1 md:mb-2">My Task</h1>
        <p className="text-sm md:text-base text-gray-600">Manage and track all your tasks</p>
      </div>

      {/* Search and Actions */}
      <div className="flex flex-col sm:flex-row gap-3 md:gap-4 mb-4 md:mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4 md:h-5 md:w-5" />
          <Input
            type="text"
            placeholder="Search your task here..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 md:pl-10 h-10 md:h-11 text-sm"
          />
        </div>
        <Button
          onClick={() => setIsCreateModalOpen(true)}
          className="bg-coral hover:bg-coral-600 gap-2 h-10 md:h-11 text-sm"
        >
          <Plus className="h-4 w-4" />
          Add Task
        </Button>
      </div>

      {/* Tasks List */}
      <div className="space-y-4">
        {isLoadingTasks ? (
          <TaskListSkeleton count={5} />
        ) : tasks.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <p className="text-gray-500 mb-2">No tasks found</p>
            <p className="text-sm text-gray-400">
              {searchTerm ? 'Try a different search term' : 'Click "Add Task" to create your first task'}
            </p>
          </div>
        ) : (
          tasks.map((task) => (
            <div
              key={task.id}
              className="bg-white rounded-lg border border-gray-200 p-4 md:p-5 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => handleTaskClick(task)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <h3 className="text-base md:text-lg font-semibold text-gray-900 mb-1 truncate">
                    {task.title}
                  </h3>
                  <p className="text-xs md:text-sm text-gray-600 line-clamp-2">
                    {task.description || 'No description provided'}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => handleEditTask(task, e)}
                  className="ml-2 flex-shrink-0"
                >
                  <Edit className="h-4 w-4" />
                </Button>
              </div>

              <div className="flex items-center gap-2 md:gap-3 flex-wrap">
                <Badge className={`${getPriorityColor(task.priority || 'medium')} border text-xs`}>
                  <Flag className="h-3 w-3 mr-1" />
                  <span className="hidden sm:inline">Priority: </span>{task.priority ? task.priority.charAt(0).toUpperCase() + task.priority.slice(1) : 'Medium'}
                </Badge>

                <Badge className={`${getStatusColor(task.status)} border text-xs`}>
                  <span className="hidden sm:inline">Status: </span>{formatStatus(task.status)}
                </Badge>

                {task.due_date && (
                  <div className="flex items-center text-xs md:text-sm text-gray-600">
                    <Calendar className="h-3 w-3 md:h-4 md:w-4 mr-1" />
                    {new Date(task.due_date).toLocaleDateString()}
                  </div>
                )}

                <div className="flex items-center text-xs md:text-sm text-gray-600">
                  <Clock className="h-3 w-3 md:h-4 md:w-4 mr-1" />
                  <span className="hidden md:inline">Created on: </span>
                  {new Date(task.created_at).toLocaleDateString()}
                </div>

                {task.tags && task.tags.length > 0 && (
                  <div className="flex items-center gap-1 flex-wrap">
                    {task.tags.slice(0, 3).map((tag) => (
                      <Badge key={tag.id} variant="outline" className="text-xs">
                        {tag.name}
                      </Badge>
                    ))}
                    {task.tags.length > 3 && (
                      <span className="text-xs text-gray-500">+{task.tags.length - 3}</span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modals */}
      <CreateTaskModal
        isOpen={isCreateModalOpen}
        onOpenChange={setIsCreateModalOpen}
        onSubmit={handleCreateTask}
        isLoading={isCreatingTask}
      />

      <EditTaskModal
        task={editingTask}
        isOpen={!!editingTask}
        onOpenChange={(open) => !open && setEditingTask(null)}
        onSubmit={handleUpdateTask}
      />

      {selectedTask && (
        <TaskDetailModal
          task={selectedTask}
          isOpen={!!selectedTask}
          onOpenChange={handleCloseModal}
          onToggleComplete={updateTaskStatus}
          onDelete={deleteTask}
        />
      )}
    </div>
  );
}

export default withAuth(MyTasksPage);
