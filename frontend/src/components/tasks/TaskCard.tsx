import { memo } from 'react';
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
  onToggleComplete: (taskId: number, status: string) => void;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: number) => void;
}

const TaskCard = memo(({ task, onToggleComplete, onEdit, onDelete }: TaskCardProps) => {
  const priorityVariant = task.priority === 'high' ? 'high' : task.priority === 'medium' ? 'medium' : 'low';

  // Use actual status field
  const statusText = task.status
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

  const statusVariant =
    task.status === 'completed' ? 'success' :
    task.status === 'in_progress' ? 'info' :
    'outline';

  const createdDate = task.created_at
    ? formatDistanceToNow(new Date(task.created_at), { addSuffix: true })
    : 'Recently';

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-3 md:p-4 mb-3 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm md:text-base font-semibold text-gray-900 mb-1 truncate">{task.title}</h3>
          {task.description && (
            <p className="text-xs md:text-sm text-gray-600 line-clamp-2 mb-2">{task.description}</p>
          )}
        </div>

        {/* Three-dot menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="h-7 w-7 md:h-8 md:w-8 p-0 flex-shrink-0 ml-2">
              <MoreVertical className="h-3 w-3 md:h-4 md:w-4 text-gray-500" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onEdit?.(task)}>
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => onToggleComplete(task.id, task.status === 'completed' ? 'not_started' : 'completed')}
            >
              {task.status === 'completed' ? 'Mark as Not Started' : 'Mark as Complete'}
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
      <div className="flex flex-wrap items-center gap-1.5 md:gap-2 mb-2">
        <Badge variant={priorityVariant} className="text-xs">{task.priority}</Badge>
        <Badge variant={statusVariant} className="text-xs">{statusText}</Badge>
        {task.tags && task.tags.length > 0 && task.tags.slice(0, 2).map((tag) => (
          <Badge key={tag.id} variant="outline" className="text-xs" style={{ borderColor: tag.color || undefined }}>
            {tag.name}
          </Badge>
        ))}
        {task.tags && task.tags.length > 2 && (
          <span className="text-xs text-gray-500">+{task.tags.length - 2}</span>
        )}
      </div>

      {/* Creation date */}
      <div className="flex items-center text-xs text-gray-500 mt-2">
        <Calendar className="h-3 w-3 mr-1" />
        <span>Created {createdDate}</span>
      </div>
    </div>
  );
});

TaskCard.displayName = 'TaskCard';

export default TaskCard;
