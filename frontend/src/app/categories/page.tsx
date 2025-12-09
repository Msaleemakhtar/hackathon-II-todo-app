"use client";

import { useState } from 'react';
import withAuth from '@/components/withAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Plus, Pencil, Trash2, FolderOpen } from 'lucide-react';

interface Category {
  id: number;
  name: string;
  type: 'priority' | 'status';
}

function CategoriesPage() {
  const [isCreatePriorityOpen, setIsCreatePriorityOpen] = useState(false);
  const [isCreateStatusOpen, setIsCreateStatusOpen] = useState(false);
  const [isEditPriorityOpen, setIsEditPriorityOpen] = useState(false);
  const [isEditStatusOpen, setIsEditStatusOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Category | null>(null);
  const [newPriority, setNewPriority] = useState('');
  const [newStatus, setNewStatus] = useState('');

  // Mock data
  const [taskPriorities, setTaskPriorities] = useState<Category[]>([
    { id: 1, name: 'Extreme', type: 'priority' },
    { id: 2, name: 'Moderate', type: 'priority' },
    { id: 3, name: 'Low', type: 'priority' },
  ]);

  const [taskStatuses, setTaskStatuses] = useState<Category[]>([
    { id: 1, name: 'Completed', type: 'status' },
    { id: 2, name: 'In Progress', type: 'status' },
    { id: 3, name: 'Not Started', type: 'status' },
  ]);

  const handleCreatePriority = () => {
    if (newPriority.trim()) {
      const newId = Math.max(...taskPriorities.map(p => p.id), 0) + 1;
      setTaskPriorities([...taskPriorities, { id: newId, name: newPriority, type: 'priority' }]);
      setNewPriority('');
      setIsCreatePriorityOpen(false);
    }
  };

  const handleCreateStatus = () => {
    if (newStatus.trim()) {
      const newId = Math.max(...taskStatuses.map(s => s.id), 0) + 1;
      setTaskStatuses([...taskStatuses, { id: newId, name: newStatus, type: 'status' }]);
      setNewStatus('');
      setIsCreateStatusOpen(false);
    }
  };

  const handleEditPriority = () => {
    if (editingItem && newPriority.trim()) {
      setTaskPriorities(
        taskPriorities.map(p => (p.id === editingItem.id ? { ...p, name: newPriority } : p))
      );
      setNewPriority('');
      setEditingItem(null);
      setIsEditPriorityOpen(false);
    }
  };

  const handleEditStatus = () => {
    if (editingItem && newStatus.trim()) {
      setTaskStatuses(
        taskStatuses.map(s => (s.id === editingItem.id ? { ...s, name: newStatus } : s))
      );
      setNewStatus('');
      setEditingItem(null);
      setIsEditStatusOpen(false);
    }
  };

  const handleDeletePriority = (id: number) => {
    if (confirm('Are you sure you want to delete this priority?')) {
      setTaskPriorities(taskPriorities.filter(p => p.id !== id));
    }
  };

  const handleDeleteStatus = (id: number) => {
    if (confirm('Are you sure you want to delete this status?')) {
      setTaskStatuses(taskStatuses.filter(s => s.id !== id));
    }
  };

  const openEditPriority = (priority: Category) => {
    setEditingItem(priority);
    setNewPriority(priority.name);
    setIsEditPriorityOpen(true);
  };

  const openEditStatus = (status: Category) => {
    setEditingItem(status);
    setNewStatus(status.name);
    setIsEditStatusOpen(true);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-2">
          <FolderOpen className="h-6 w-6 text-coral" />
          <h1 className="text-2xl font-bold text-gray-900">Task Categories</h1>
        </div>
        <p className="text-gray-600">Manage task priorities and statuses</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Task Priorities */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Task Priority</h2>
            <Button
              onClick={() => setIsCreatePriorityOpen(true)}
              size="sm"
              className="bg-coral hover:bg-coral-600 gap-2"
            >
              <Plus className="h-4 w-4" />
              Add Category
            </Button>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-16">SN</TableHead>
                <TableHead>Task Priority</TableHead>
                <TableHead className="w-24 text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {taskPriorities.map((priority, index) => (
                <TableRow key={priority.id}>
                  <TableCell className="font-medium">{index + 1}</TableCell>
                  <TableCell>{priority.name}</TableCell>
                  <TableCell>
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => openEditPriority(priority)}
                        className="h-8 w-8 p-0"
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleDeletePriority(priority.id)}
                        className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Task Statuses */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Task Status</h2>
            <Button
              onClick={() => setIsCreateStatusOpen(true)}
              size="sm"
              className="bg-coral hover:bg-coral-600 gap-2"
            >
              <Plus className="h-4 w-4" />
              Add Category
            </Button>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-16">SN</TableHead>
                <TableHead>Task Status</TableHead>
                <TableHead className="w-24 text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {taskStatuses.map((status, index) => (
                <TableRow key={status.id}>
                  <TableCell className="font-medium">{index + 1}</TableCell>
                  <TableCell>{status.name}</TableCell>
                  <TableCell>
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => openEditStatus(status)}
                        className="h-8 w-8 p-0"
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleDeleteStatus(status.id)}
                        className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* Create Priority Modal */}
      <Dialog open={isCreatePriorityOpen} onOpenChange={setIsCreatePriorityOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Task Priority</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="priority-title">Title</Label>
              <Input
                id="priority-title"
                placeholder="Enter priority name"
                value={newPriority}
                onChange={(e) => setNewPriority(e.target.value)}
                className="h-11"
              />
            </div>
            <div className="flex gap-3">
              <Button onClick={handleCreatePriority} className="flex-1 bg-coral hover:bg-coral-600">
                Create
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setNewPriority('');
                  setIsCreatePriorityOpen(false);
                }}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Create Status Modal */}
      <Dialog open={isCreateStatusOpen} onOpenChange={setIsCreateStatusOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Task Status</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="status-name">Name</Label>
              <Input
                id="status-name"
                placeholder="Enter status name"
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value)}
                className="h-11"
              />
            </div>
            <div className="flex gap-3">
              <Button onClick={handleCreateStatus} className="flex-1 bg-coral hover:bg-coral-600">
                Create
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setNewStatus('');
                  setIsCreateStatusOpen(false);
                }}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit Priority Modal */}
      <Dialog open={isEditPriorityOpen} onOpenChange={setIsEditPriorityOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Task Priority</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-priority-title">Title</Label>
              <Input
                id="edit-priority-title"
                placeholder="Enter priority name"
                value={newPriority}
                onChange={(e) => setNewPriority(e.target.value)}
                className="h-11"
              />
            </div>
            <div className="flex gap-3">
              <Button onClick={handleEditPriority} className="flex-1 bg-coral hover:bg-coral-600">
                Update
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setNewPriority('');
                  setEditingItem(null);
                  setIsEditPriorityOpen(false);
                }}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit Status Modal */}
      <Dialog open={isEditStatusOpen} onOpenChange={setIsEditStatusOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Task Status</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-status-name">Name</Label>
              <Input
                id="edit-status-name"
                placeholder="Enter status name"
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value)}
                className="h-11"
              />
            </div>
            <div className="flex gap-3">
              <Button onClick={handleEditStatus} className="flex-1 bg-coral hover:bg-coral-600">
                Update
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setNewStatus('');
                  setEditingItem(null);
                  setIsEditStatusOpen(false);
                }}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default withAuth(CategoriesPage);
