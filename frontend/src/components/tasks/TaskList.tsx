/**
 * TaskList - Smart task list component with automatic performance optimization (T032, US2)
 *
 * Automatically switches between simple grid layout and virtual scrolling
 * based on the number of tasks to optimize performance.
 *
 * Performance strategy:
 * - Small lists (<100 tasks): Simple grid layout for better UX
 * - Large lists (>=100 tasks): Virtual scrolling for 60fps performance
 */

import { Task } from '@/types';
import TaskCard from './TaskCard';
import VirtualizedTaskList from './VirtualizedTaskList';

type TaskDisplay = Task & {
  ui_status: 'Not Started' | 'In Progress' | 'Completed';
  is_loading: boolean;
};

interface TaskListProps {
  tasks: TaskDisplay[];
  onToggleComplete: (taskId: number, status: string) => void;
  /**
   * Threshold for switching to virtual scrolling (default: 100)
   * Set to Infinity to always use grid layout
   * Set to 0 to always use virtual scrolling
   */
  virtualScrollThreshold?: number;
}

const TaskList = ({
  tasks,
  onToggleComplete,
  virtualScrollThreshold = 100,
}: TaskListProps) => {
  // Empty state
  if (tasks.length === 0) {
    return (
      <div className="text-center py-10">
        <h2 className="text-2xl font-bold mb-2">No tasks found</h2>
        <p className="text-gray-500">Start by creating a new task!</p>
      </div>
    );
  }

  // For large lists, use virtual scrolling for better performance (FR-016)
  if (tasks.length >= virtualScrollThreshold) {
    return <VirtualizedTaskList tasks={tasks} onToggleComplete={onToggleComplete} />;
  }

  // For small lists, use simple grid layout for better UX
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {tasks.map((task) => (
        <TaskCard key={task.id} task={task} onToggleComplete={onToggleComplete} />
      ))}
    </div>
  );
};

export default TaskList;
