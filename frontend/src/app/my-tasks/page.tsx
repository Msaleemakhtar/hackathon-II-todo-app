"use client";

import { useState } from 'react';
import { useTasks } from '@/hooks/useTasks';
import withAuth from '@/components/withAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Calendar, Clock, Flag, Search, Plus } from 'lucide-react';
import CreateTaskModal from '@/components/tasks/CreateTaskModal';
import TaskDetailModal from '@/components/tasks/TaskDetailModal';

function MyTasksPage() {
  const { tasks, isLoadingTasks, updateTaskStatus, createTask, deleteTask } = useTasks();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const handleCreateTask = async (taskData: { title: string; description: string; priority: 'low' | 'medium' | 'high'; dueDate: string }) => {
    await createTask(taskData);
    setIsCreateModalOpen(false);
  };

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

  const getStatusColor = (completed: boolean) => {
    return completed
      ? 'bg-green-100 text-green-700 border-green-200'
      : 'bg-yellow-100 text-yellow-700 border-yellow-200';
  };

  const filteredTasks = tasks.filter(task =>
    task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    task.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoadingTasks) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coral mx-auto mb-4"></div>
          <p className="text-gray-600">Loading tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">My Task</h1>
        <p className="text-gray-600">Manage and track all your tasks</p>
      </div>

      {/* Search and Actions */}
      <div className="flex gap-4 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          <Input
            type="text"
            placeholder="Search your task here..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 h-11"
          />
        </div>
        <Button
          onClick={() => setIsCreateModalOpen(true)}
          className="bg-coral hover:bg-coral-600 gap-2"
        >
          <Plus className="h-4 w-4" />
          Add Task
        </Button>
      </div>

      {/* Tasks List */}
      <div className="space-y-4">
        {filteredTasks.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <p className="text-gray-500 mb-2">No tasks found</p>
            <p className="text-sm text-gray-400">
              {searchQuery ? 'Try a different search term' : 'Click "Add Task" to create your first task'}
            </p>
          </div>
        ) : (
          filteredTasks.map((task) => (
            <div
              key={task.id}
              className="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setSelectedTask(task)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {task.title}
                  </h3>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {task.description || 'No description provided'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 flex-wrap">
                <Badge className={`${getPriorityColor(task.priority || 'medium')} border`}>
                  <Flag className="h-3 w-3 mr-1" />
                  Priority: {task.priority ? task.priority.charAt(0).toUpperCase() + task.priority.slice(1) : 'Medium'}
                </Badge>

                <Badge className={`${getStatusColor(task.completed)} border`}>
                  Status: {task.completed ? 'Completed' : 'In Progress'}
                </Badge>

                {task.due_date && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Calendar className="h-4 w-4 mr-1" />
                    {new Date(task.due_date).toLocaleDateString()}
                  </div>
                )}

                <div className="flex items-center text-sm text-gray-600">
                  <Clock className="h-4 w-4 mr-1" />
                  Created on: {new Date(task.created_at).toLocaleDateString()}
                </div>
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
      />

      {selectedTask && (
        <TaskDetailModal
          task={selectedTask}
          isOpen={!!selectedTask}
          onOpenChange={(open) => !open && setSelectedTask(null)}
          onToggleComplete={updateTaskStatus}
          onDelete={deleteTask}
        />
      )}
    </div>
  );
}

export default withAuth(MyTasksPage);
