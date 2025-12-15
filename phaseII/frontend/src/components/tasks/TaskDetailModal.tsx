import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar, Clock, Flag, CheckCircle2, Trash2, X, Tag as TagIcon } from 'lucide-react';
import { useState } from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

interface TaskDetailModalProps {
  task: any;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onToggleComplete: (taskId: number, status: string) => void;
  onDelete: (taskId: number) => void;
}

const TaskDetailModal = ({
  task,
  isOpen,
  onOpenChange,
  onToggleComplete,
  onDelete
}: TaskDetailModalProps) => {
  const [isUpdating, setIsUpdating] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  if (!task) return null;

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

  const handleToggleComplete = async () => {
    setIsUpdating(true);
    try {
      await onToggleComplete(task.id, task.status === 'completed' ? 'not_started' : 'completed');
      // Give a small delay for the state to update before allowing another action
      setTimeout(() => setIsUpdating(false), 500);
    } catch (error) {
      console.error('Failed to toggle task status:', error);
      setIsUpdating(false);
    }
  };

  const handleDelete = () => {
    onDelete(task.id);
    onOpenChange(false);
  };

  const handleDeleteWithConfirmation = () => {
    setShowDeleteDialog(false);
    onDelete(task.id);
    onOpenChange(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <DialogTitle className="text-2xl font-bold pr-8">{task.title}</DialogTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onOpenChange(false)}
              className="absolute right-4 top-4"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Status and Priority Badges */}
          <div className="flex items-center gap-3 flex-wrap">
            <Badge className={`${getPriorityColor(task.priority || 'medium')} border`}>
              <Flag className="h-3 w-3 mr-1" />
              Priority: {task.priority ? task.priority.charAt(0).toUpperCase() + task.priority.slice(1) : 'Medium'}
            </Badge>

            <Badge className={task.status === 'completed' ? 'bg-green-100 text-green-700 border-green-200 border' : 'bg-yellow-100 text-yellow-700 border-yellow-200 border'}>
              Status: {task.status.split('_').map((w: string) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
            </Badge>
          </div>

          {/* Dates */}
          <div className="space-y-2">
            <div className="flex items-center text-sm text-gray-600">
              <Calendar className="h-4 w-4 mr-2" />
              <span className="font-medium mr-2">Created on:</span>
              {new Date(task.created_at).toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </div>

            {task.due_date && (
              <div className="flex items-center text-sm text-gray-600">
                <Clock className="h-4 w-4 mr-2" />
                <span className="font-medium mr-2">Due Date:</span>
                {new Date(task.due_date).toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </div>
            )}
          </div>

          {/* Description */}
          <div>
            <h3 className="text-lg font-semibold mb-3 text-gray-900">Task Description</h3>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <p className="text-gray-700 whitespace-pre-wrap">
                {task.description || 'No description provided for this task.'}
              </p>
            </div>
          </div>

          {/* Tags Section */}
          {task.tags && task.tags.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3 text-gray-900">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {task.tags.map((tag: any) => (
                  <Badge key={tag.id} className="bg-blue-100 text-blue-700 border-blue-200 border">
                    <TagIcon className="h-3 w-3 mr-1" />
                    {tag.name}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <Button
              onClick={handleToggleComplete}
              disabled={isUpdating}
              className={task.completed ? 'flex-1 bg-gray-600 hover:bg-gray-700' : 'flex-1 bg-green-600 hover:bg-green-700'}
            >
              {isUpdating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Updating...
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                  {task.completed ? 'Mark as Pending' : 'Mark as Complete'}
                </>
              )}
            </Button>

            <Button
              onClick={() => setShowDeleteDialog(true)}
              variant="destructive"
              className="flex-1"
              disabled={isUpdating}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete Task
            </Button>
          </div>

          <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Are you sure you want to delete this task?</AlertDialogTitle>
                <AlertDialogDescription>
                  This action cannot be undone. This will permanently delete the task "{task.title}"
                  and remove it from your task list.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={handleDeleteWithConfirmation}
                  className="bg-destructive hover:bg-destructive/90"
                >
                  Delete Task
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>

          <Button
            onClick={() => onOpenChange(false)}
            variant="outline"
            className="w-full"
          >
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default TaskDetailModal;
