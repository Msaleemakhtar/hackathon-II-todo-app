import { Task } from '@/types';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { MoreVertical, Calendar } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface TaskCardProps {
  task: Task;
  onToggleComplete: (taskId: number, completed: boolean) => void;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: number) => void;
}

const TaskCard = ({ task, onToggleComplete, onEdit, onDelete }: TaskCardProps) => {
  const priorityVariant = task.priority === 'high' ? 'high' : task.priority === 'medium' ? 'medium' : 'low';

  const statusVariant = task.completed
    ? 'success'
    : task.is_loading
    ? 'info'
    : 'outline';

  const statusText = task.completed
    ? 'Completed'
    : task.is_loading
    ? 'In Progress'
    : 'Not Started';

  const createdDate = task.created_at
    ? formatDistanceToNow(new Date(task.created_at), { addSuffix: true })
    : 'Recently';

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-3 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <h3 className="text-base font-semibold text-gray-900 mb-1">{task.title}</h3>
          {task.description && (
            <p className="text-sm text-gray-600 line-clamp-2 mb-2">{task.description}</p>
          )}
        </div>

        {/* Three-dot menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
              <MoreVertical className="h-4 w-4 text-gray-500" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onEdit?.(task)}>
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => onToggleComplete(task.id, !task.completed)}
            >
              {task.completed ? 'Mark as Incomplete' : 'Mark as Complete'}
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => onDelete?.(task.id)}
              className="text-error"
            >
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Task metadata */}
      <div className="flex flex-wrap items-center gap-2 mb-2">
        <Badge variant={priorityVariant}>{task.priority}</Badge>
        <Badge variant={statusVariant}>{statusText}</Badge>
      </div>

      {/* Creation date */}
      <div className="flex items-center text-xs text-gray-500 mt-2">
        <Calendar className="h-3 w-3 mr-1" />
        <span>Created {createdDate}</span>
      </div>
    </div>
  );
};

export default TaskCard;
