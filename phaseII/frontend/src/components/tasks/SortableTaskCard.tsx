'use client';

import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical } from 'lucide-react';
import { Task } from '@/types';
import TaskCard from './TaskCard';

interface SortableTaskCardProps {
  task: Task;
  onToggleComplete: (taskId: number, status: string) => void;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: number) => void;
  className?: string;
  isUpdating?: boolean;
  isDeleting?: boolean;
}

export function SortableTaskCard({
  task,
  onToggleComplete,
  onEdit,
  onDelete,
  className = '',
  isUpdating = false,
  isDeleting = false,
}: SortableTaskCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`relative ${className}`}
    >
      {/* Drag Handle */}
      <button
        {...attributes}
        {...listeners}
        className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-2 p-1 cursor-grab active:cursor-grabbing hover:bg-gray-100 rounded touch-none focus:outline-none focus:ring-2 focus:ring-coral z-10"
        aria-label="Drag to reorder task"
        tabIndex={0}
      >
        <GripVertical className="h-4 w-4 text-gray-400 hover:text-gray-600" />
      </button>

      {/* Task Card */}
      <TaskCard
        task={task}
        onToggleComplete={onToggleComplete}
        onEdit={onEdit}
        onDelete={onDelete}
        className={`ml-6 ${isDragging ? 'shadow-xl ring-2 ring-coral' : ''}`}
        isUpdating={isUpdating}
        isDeleting={isDeleting}
      />
    </div>
  );
}
