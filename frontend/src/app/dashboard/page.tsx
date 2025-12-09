"use client";

import { useState } from 'react';
import { useTasks } from '@/hooks/useTasks';
import TaskCard from '@/components/tasks/TaskCard';
import TaskStatusChart from '@/components/dashboard/TaskStatusChart';
import CompletedTaskList from '@/components/tasks/CompletedTaskList';
import CreateTaskModal from '@/components/tasks/CreateTaskModal';
import withAuth from '@/components/withAuth';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Plus, UserPlus } from 'lucide-react';

function DashboardPage() {
  const { tasks, isLoadingTasks, updateTaskStatus, createTask, deleteTask } = useTasks();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Mock user data
  const user = {
    name: "John Doe",
    firstName: "John"
  };

  // Mock team members
  const teamMembers = [
    { id: '1', name: 'Alice Johnson', avatar: '', initials: 'AJ' },
    { id: '2', name: 'Bob Smith', avatar: '', initials: 'BS' },
    { id: '3', name: 'Carol White', avatar: '', initials: 'CW' },
  ];

  const handleCreateTask = async (taskData: { title: string; description: string; priority: 'low' | 'medium' | 'high'; dueDate: string }) => {
    await createTask(taskData);
    setIsCreateModalOpen(false);
  };

  const handleDeleteTask = async (taskId: number) => {
    if (confirm('Are you sure you want to delete this task?')) {
      await deleteTask(taskId);
    }
  };

  const handleRestoreTask = async (taskId: number) => {
    await updateTaskStatus(taskId, false);
  };

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

  const pendingTasks = tasks.filter(t => !t.completed);
  const currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric'
  });

  return (
    <div className="p-6 space-y-6">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">
            Welcome back, {user.firstName}! 👋
          </h1>
          <p className="text-sm text-gray-600">Here&apos;s what&apos;s happening with your tasks today.</p>
        </div>

        {/* Team Members */}
        <div className="flex items-center gap-3">
          <div className="flex -space-x-2">
            {teamMembers.map((member) => (
              <Avatar key={member.id} className="h-8 w-8 border-2 border-white">
                <AvatarImage src={member.avatar} alt={member.name} />
                <AvatarFallback className="bg-coral text-white text-xs">{member.initials}</AvatarFallback>
              </Avatar>
            ))}
          </div>
          <Button variant="outline" size="sm" className="gap-2">
            <UserPlus className="h-4 w-4" />
            Invite
          </Button>
        </div>
      </div>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel - To-Do Section */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">To-Do</h2>
                <p className="text-sm text-gray-600">{currentDate} · Today</p>
              </div>
              <Button
                onClick={() => setIsCreateModalOpen(true)}
                className="gap-2 bg-coral hover:bg-coral-600"
              >
                <Plus className="h-4 w-4" />
                Add Task
              </Button>
            </div>

            {/* Task List */}
            <div className="space-y-3">
              {pendingTasks.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <p className="mb-2">No tasks yet</p>
                  <p className="text-sm">Click &quot;Add Task&quot; to create your first task</p>
                </div>
              ) : (
                pendingTasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onToggleComplete={updateTaskStatus}
                    onDelete={handleDeleteTask}
                  />
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Panel */}
        <div className="space-y-6">
          {/* Task Status Chart */}
          <TaskStatusChart tasks={tasks} />

          {/* Completed Tasks Section */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="h-8 w-1 bg-coral rounded" />
              <h2 className="text-lg font-semibold text-gray-900">Completed Task</h2>
            </div>
            <CompletedTaskList
              tasks={tasks}
              onRestore={handleRestoreTask}
              onDelete={handleDeleteTask}
            />
          </div>
        </div>
      </div>

      {/* Create Task Modal */}
      <CreateTaskModal
        isOpen={isCreateModalOpen}
        onOpenChange={setIsCreateModalOpen}
        onSubmit={handleCreateTask}
      />
    </div>
  );
}

export default withAuth(DashboardPage);
