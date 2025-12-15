'use client';

import { useRef } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { Task } from '@/types';
import TaskCard from './TaskCard';

type TaskDisplay = Task & {
  ui_status: 'Not Started' | 'In Progress' | 'Completed';
  is_loading: boolean;
};

interface VirtualizedTaskListProps {
  tasks: TaskDisplay[];
  onToggleComplete: (taskId: number, status: string) => void;
}

/**
 * VirtualizedTaskList - High-performance task list component (FR-016, US2)
 *
 * Uses @tanstack/react-virtual for efficient rendering of 10,000+ tasks.
 * Only renders visible items in the viewport, significantly reducing DOM nodes.
 *
 * Performance characteristics:
 * - Renders only ~10-20 items at a time regardless of total count
 * - Smooth 60fps scrolling even with 100k+ items
 * - Memory footprint stays constant with list size
 *
 * @param tasks - Array of tasks to display
 * @param onToggleComplete - Callback when task completion status changes
 */
const VirtualizedTaskList = ({ tasks, onToggleComplete }: VirtualizedTaskListProps) => {
  const parentRef = useRef<HTMLDivElement>(null);

  // Configure virtualizer with optimized settings
  const rowVirtualizer = useVirtualizer({
    count: tasks.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 200, // Estimated height of each task card in pixels
    overscan: 5, // Render 5 extra items above/below viewport for smooth scrolling
    gap: 16, // Gap between items (matching grid gap-4 = 16px)
  });

  if (tasks.length === 0) {
    return (
      <div className="text-center py-10">
        <h2 className="text-2xl font-bold mb-2">No tasks found</h2>
        <p className="text-gray-500">Start by creating a new task!</p>
      </div>
    );
  }

  return (
    <div
      ref={parentRef}
      className="h-[calc(100vh-200px)] overflow-auto" // Fixed height container for scrolling
      style={{
        contain: 'strict', // CSS containment for better performance
      }}
    >
      <div
        style={{
          height: `${rowVirtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {rowVirtualizer.getVirtualItems().map((virtualItem) => {
          const task = tasks[virtualItem.index];
          return (
            <div
              key={virtualItem.key}
              data-index={virtualItem.index}
              ref={rowVirtualizer.measureElement}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                transform: `translateY(${virtualItem.start}px)`,
              }}
            >
              <div className="px-4">
                <TaskCard
                  task={task}
                  onToggleComplete={onToggleComplete}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default VirtualizedTaskList;
