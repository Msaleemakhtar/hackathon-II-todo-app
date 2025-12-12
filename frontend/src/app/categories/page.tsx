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
import { Plus, Pencil, Trash2, FolderOpen, Loader2 } from 'lucide-react';
import { useCategories, Category } from '@/hooks/useCategories';

function CategoriesPage() {
  const {
    taskPriorities,
    taskStatuses,
    isLoadingPriorities,
    isLoadingStatuses,
    error,
    addPriority,
    addStatus,
    updatePriority,
    updateStatus,
    deletePriority,
    deleteStatus,
  } = useCategories();

  const [isCreatePriorityOpen, setIsCreatePriorityOpen] = useState(false);
  const [isCreateStatusOpen, setIsCreateStatusOpen] = useState(false);
  const [isEditPriorityOpen, setIsEditPriorityOpen] = useState(false);
  const [isEditStatusOpen, setIsEditStatusOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Category | null>(null);
  const [newPriority, setNewPriority] = useState('');
  const [newStatus, setNewStatus] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCreatePriority = async () => {
    if (!newPriority.trim()) return;

    setIsSubmitting(true);
    try {
      await addPriority(newPriority);
      setNewPriority('');
      setIsCreatePriorityOpen(false);
    } catch (err) {
      console.error('Failed to create priority:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreateStatus = async () => {
    if (!newStatus.trim()) return;

    setIsSubmitting(true);
    try {
      await addStatus(newStatus);
      setNewStatus('');
      setIsCreateStatusOpen(false);
    } catch (err) {
      console.error('Failed to create status:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditPriority = async () => {
    if (!editingItem || !newPriority.trim()) return;

    setIsSubmitting(true);
    try {
      await updatePriority(editingItem.id, newPriority);
      setNewPriority('');
      setEditingItem(null);
      setIsEditPriorityOpen(false);
    } catch (err) {
      console.error('Failed to update priority:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditStatus = async () => {
    if (!editingItem || !newStatus.trim()) return;

    setIsSubmitting(true);
    try {
      await updateStatus(editingItem.id, newStatus);
      setNewStatus('');
      setEditingItem(null);
      setIsEditStatusOpen(false);
    } catch (err) {
      console.error('Failed to update status:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeletePriority = async (id: number) => {
    if (!confirm('Are you sure you want to delete this priority?')) return;

    try {
      await deletePriority(id);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to delete priority.';
      alert(errorMessage);
    }
  };

  const handleDeleteStatus = async (id: number) => {
    if (!confirm('Are you sure you want to delete this status?')) return;

    try {
      await deleteStatus(id);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to delete status.';
      alert(errorMessage);
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
    <div className="p-4 md:p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-4 md:mb-6">
        <div className="flex items-center gap-2 mb-2">
          <FolderOpen className="h-5 w-5 md:h-6 md:w-6 text-coral" />
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">Task Categories</h1>
        </div>
        <p className="text-sm md:text-base text-gray-600">Manage task priorities and statuses</p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        {/* Task Priorities */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 md:p-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-3">
            <h2 className="text-base md:text-lg font-semibold text-gray-900">Task Priority</h2>
            <Button
              onClick={() => setIsCreatePriorityOpen(true)}
              size="sm"
              className="bg-coral hover:bg-coral-600 gap-2 w-full sm:w-auto text-xs md:text-sm"
            >
              <Plus className="h-4 w-4" />
              <span className="hidden sm:inline">Add Category</span>
              <span className="sm:hidden">Add</span>
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
              {isLoadingPriorities ? (
                <TableRow>
                  <TableCell colSpan={3} className="text-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin mx-auto text-gray-400" />
                    <p className="text-sm text-gray-500 mt-2">Loading priorities...</p>
                  </TableCell>
                </TableRow>
              ) : !taskPriorities || taskPriorities.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={3} className="text-center py-8 text-gray-500">
                    No priorities found. Create your first priority!
                  </TableCell>
                </TableRow>
              ) : (
                taskPriorities.map((priority, index) => (
                  <TableRow key={priority.id}>
                    <TableCell className="font-medium">{index + 1}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {priority.name}
                        {priority.is_default && (
                          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">Default</span>
                        )}
                      </div>
                    </TableCell>
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
                          disabled={priority.is_default}
                          title={priority.is_default ? 'Cannot delete default priority' : 'Delete priority'}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {/* Task Statuses */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 md:p-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-3">
            <h2 className="text-base md:text-lg font-semibold text-gray-900">Task Status</h2>
            <Button
              onClick={() => setIsCreateStatusOpen(true)}
              size="sm"
              className="bg-coral hover:bg-coral-600 gap-2 w-full sm:w-auto text-xs md:text-sm"
            >
              <Plus className="h-4 w-4" />
              <span className="hidden sm:inline">Add Category</span>
              <span className="sm:hidden">Add</span>
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
              {isLoadingStatuses ? (
                <TableRow>
                  <TableCell colSpan={3} className="text-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin mx-auto text-gray-400" />
                    <p className="text-sm text-gray-500 mt-2">Loading statuses...</p>
                  </TableCell>
                </TableRow>
              ) : !taskStatuses || taskStatuses.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={3} className="text-center py-8 text-gray-500">
                    No statuses found. Create your first status!
                  </TableCell>
                </TableRow>
              ) : (
                taskStatuses.map((status, index) => (
                  <TableRow key={status.id}>
                    <TableCell className="font-medium">{index + 1}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {status.name}
                        {status.is_default && (
                          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">Default</span>
                        )}
                      </div>
                    </TableCell>
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
                          disabled={status.is_default}
                          title={status.is_default ? 'Cannot delete default status' : 'Delete status'}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
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
              <Button
                onClick={handleCreatePriority}
                className="flex-1 bg-coral hover:bg-coral-600"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create'
                )}
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setNewPriority('');
                  setIsCreatePriorityOpen(false);
                }}
                className="flex-1"
                disabled={isSubmitting}
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
              <Button
                onClick={handleCreateStatus}
                className="flex-1 bg-coral hover:bg-coral-600"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create'
                )}
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setNewStatus('');
                  setIsCreateStatusOpen(false);
                }}
                className="flex-1"
                disabled={isSubmitting}
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
              <Button
                onClick={handleEditPriority}
                className="flex-1 bg-coral hover:bg-coral-600"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Updating...
                  </>
                ) : (
                  'Update'
                )}
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setNewPriority('');
                  setEditingItem(null);
                  setIsEditPriorityOpen(false);
                }}
                className="flex-1"
                disabled={isSubmitting}
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
              <Button
                onClick={handleEditStatus}
                className="flex-1 bg-coral hover:bg-coral-600"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Updating...
                  </>
                ) : (
                  'Update'
                )}
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  setNewStatus('');
                  setEditingItem(null);
                  setIsEditStatusOpen(false);
                }}
                className="flex-1"
                disabled={isSubmitting}
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
