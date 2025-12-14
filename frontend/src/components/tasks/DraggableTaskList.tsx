'use client';

import { useState, useEffect } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { Task } from '@/types';
import { SortableTaskCard } from './SortableTaskCard';
import TaskCard from './TaskCard';

interface DraggableTaskListProps {
  tasks: Task[];
  onToggleComplete: (taskId: number, status: string) => void;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: number) => void;
  onReorder: (taskIds: number[]) => Promise<void>;
  isUpdating?: boolean;
  isDeleting?: boolean;
  // Per-task loading state functions
  isTaskUpdating?: (taskId: number) => boolean;
  isTaskDeleting?: (taskId: number) => boolean;
}

export function DraggableTaskList({
  tasks,
  onToggleComplete,
  onEdit,
  onDelete,
  onReorder,
  isUpdating = false,
  isDeleting = false,
  isTaskUpdating,
  isTaskDeleting,
}: DraggableTaskListProps) {
  const [activeId, setActiveId] = useState<number | null>(null);
  const [items, setItems] = useState(tasks);

  // Update items when tasks prop changes
  useEffect(() => {
    setItems(tasks);
  }, [tasks]);

  // Configure sensors for drag detection
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px of movement required before drag starts
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as number);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (!over || active.id === over.id) {
      setActiveId(null);
      return;
    }

    const oldIndex = items.findIndex((item) => item.id === active.id);
    const newIndex = items.findIndex((item) => item.id === over.id);

    if (oldIndex !== -1 && newIndex !== -1) {
      // Optimistically update the UI
      const newItems = arrayMove(items, oldIndex, newIndex);
      setItems(newItems);

      // Persist the new order to the backend
      const taskIds = newItems.map((task) => task.id);
      onReorder(taskIds).catch((error) => {
        console.error('Failed to persist task order:', error);
        // Revert on error
        setItems(items);
      });
    }

    setActiveId(null);
  };

  const handleDragCancel = () => {
    setActiveId(null);
  };

  const activeTask = activeId ? items.find((task) => task.id === activeId) : null;

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragCancel={handleDragCancel}
    >
      <SortableContext
        items={items.map((task) => task.id)}
        strategy={verticalListSortingStrategy}
      >
        <div className="space-y-3">
          {items.map((task) => (
            <SortableTaskCard
              key={task.id}
              task={task}
              onToggleComplete={onToggleComplete}
              onEdit={onEdit}
              onDelete={onDelete}
              isUpdating={isTaskUpdating ? isTaskUpdating(task.id) : isUpdating}
              isDeleting={isTaskDeleting ? isTaskDeleting(task.id) : isDeleting}
            />
          ))}
        </div>
      </SortableContext>

      {/* Drag Overlay - Shows dragged item while dragging */}
      <DragOverlay>
        {activeTask ? (
          <div className="transform rotate-3">
            <TaskCard
              task={activeTask}
              onToggleComplete={onToggleComplete}
              className="shadow-2xl ring-2 ring-coral cursor-grabbing"
              isUpdating={isTaskUpdating ? isTaskUpdating(activeTask.id) : isUpdating}
              isDeleting={isTaskDeleting ? isTaskDeleting(activeTask.id) : isDeleting}
            />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
