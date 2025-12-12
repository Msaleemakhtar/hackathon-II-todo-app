import { Task } from '@/types';
import TaskCard from './TaskCard';

type TaskDisplay = Task & {
  ui_status: 'Not Started' | 'In Progress' | 'Completed';
  is_loading: boolean;
};

interface TaskListProps {
  tasks: TaskDisplay[];
  onToggleComplete: (taskId: number, status: string) => void;
}

const TaskList = ({ tasks, onToggleComplete }: TaskListProps) => {
  if (tasks.length === 0) {
    return (
      <div className="text-center py-10">
        <h2 className="text-2xl font-bold mb-2">No tasks found</h2>
        <p className="text-gray-500">Start by creating a new task!</p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {tasks.map((task) => (
        <TaskCard key={task.id} task={task} onToggleComplete={onToggleComplete} />
      ))}
    </div>
  );
};

export default TaskList;
