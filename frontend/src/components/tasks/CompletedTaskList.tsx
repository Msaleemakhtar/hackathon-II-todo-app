import { Task } from '@/types';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { MoreVertical, CheckCircle2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface CompletedTaskListProps {
  tasks: Task[];
  onRestore?: (taskId: number) => void;
  onDelete?: (taskId: number) => void;
  isUpdating?: boolean;
  isDeleting?: boolean;
  // Per-task loading state functions
  isTaskUpdating?: (taskId: number) => boolean;
  isTaskDeleting?: (taskId: number) => boolean;
}

const CompletedTaskList = ({
  tasks,
  onRestore,
  onDelete,
  isUpdating = false,
  isDeleting = false,
  isTaskUpdating,
  isTaskDeleting,
}: CompletedTaskListProps) => {
  const completedTasks = tasks
    .filter(task => task.status === 'completed')
    .sort((a, b) => {
      // Sort by updated_at in descending order (most recently completed first)
      return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
    });

  if (completedTasks.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <CheckCircle2 className="h-12 w-12 mx-auto mb-3 text-gray-300" />
        <p className="text-sm">No completed tasks yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {completedTasks.map((task) => {
        const completedDate = task.updated_at
          ? `Completed ${formatDistanceToNow(new Date(task.updated_at), { addSuffix: true })}`
          : 'Recently completed';

        // Use per-task loading state if available, fallback to global state
        const taskIsUpdating = isTaskUpdating ? isTaskUpdating(task.id) : isUpdating;
        const taskIsDeleting = isTaskDeleting ? isTaskDeleting(task.id) : isDeleting;
        const taskIsOperating = taskIsUpdating || taskIsDeleting;

        return (
          <div
            key={task.id}
            className={`bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-all ${
              taskIsOperating ? 'opacity-70' : ''
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="text-sm font-semibold text-gray-900">{task.title}</h4>
                  <Badge variant="success" className="text-xs">Completed</Badge>
                </div>
                {task.description && (
                  <p className="text-xs text-gray-600 line-clamp-1 mb-2">{task.description}</p>
                )}
                <p className="text-xs text-gray-500">{completedDate}</p>
              </div>

              {/* Three-dot menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-8 w-8 p-0" disabled={taskIsOperating}>
                    {taskIsOperating ? (
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-400 border-t-transparent" />
                    ) : (
                      <MoreVertical className="h-4 w-4 text-gray-500" />
                    )}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => onRestore?.(task.id)} disabled={taskIsOperating}>
                    {taskIsUpdating ? (
                      <>
                        <div className="h-3 w-3 mr-2 animate-spin rounded-full border-2 border-gray-600 border-t-transparent" />
                        Restoring...
                      </>
                    ) : (
                      'Restore to Pending'
                    )}
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => onDelete?.(task.id)}
                    className="text-error"
                    disabled={taskIsOperating}
                  >
                    {taskIsDeleting ? (
                      <>
                        <div className="h-3 w-3 mr-2 animate-spin rounded-full border-2 border-red-600 border-t-transparent" />
                        Deleting...
                      </>
                    ) : (
                      'Delete'
                    )}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default CompletedTaskList;
