import React, { useState, useEffect } from 'react';
import { Task } from '@/types';
import { useTags } from '@/hooks/useTags';
import { useCategories } from '@/hooks/useCategories';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { X, Tags, Calendar, Flag, AlertCircle, CheckCircle2, Sparkles, Plus } from 'lucide-react';

interface EditTaskFormProps {
  task: Task;
  onSubmit: (taskData: { title: string; description: string; priority: string; dueDate: string; tagIds: number[] }) => void;
  isLoading?: boolean;
}

const EditTaskForm = ({ task, onSubmit, isLoading }: EditTaskFormProps) => {
  const { tags, isLoadingTags, createTag } = useTags();
  const { taskPriorities, isLoadingPriorities } = useCategories();
  const [title, setTitle] = useState(task.title || '');
  const [description, setDescription] = useState(task.description || '');
  const [priority, setPriority] = useState(task.priority || '');
  const [dueDate, setDueDate] = useState(
    task.due_date ? new Date(task.due_date).toISOString().split('T')[0] : ''
  );
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>(
    task.tags?.map(tag => tag.id) || []
  );
  const [newTagName, setNewTagName] = useState('');
  const [isCreatingTag, setIsCreatingTag] = useState(false);

  useEffect(() => {
    setTitle(task.title || '');
    setDescription(task.description || '');
    setPriority(task.priority || '');
    setDueDate(task.due_date ? new Date(task.due_date).toISOString().split('T')[0] : '');
    setSelectedTagIds(task.tags?.map(tag => tag.id) || []);
  }, [task]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit({ title, description, priority, dueDate, tagIds: selectedTagIds });
  };

  const toggleTag = (tagId: number) => {
    setSelectedTagIds((prev) =>
      prev.includes(tagId)
        ? prev.filter((id) => id !== tagId)
        : [...prev, tagId]
    );
  };

  const handleCreateTag = async () => {
    if (!newTagName.trim()) return;

    setIsCreatingTag(true);
    try {
      const newTag = await createTag({ name: newTagName.trim() });
      // Add to selected tags immediately
      if (newTag && newTag.id) {
        setSelectedTagIds((prev) => {
          // Prevent duplicates
          if (prev.includes(newTag.id)) return prev;
          return [...prev, newTag.id];
        });
      }
      setNewTagName('');
    } catch (err) {
      console.error('Failed to create tag:', err);
      alert('Failed to create tag. Please try again.');
    } finally {
      setIsCreatingTag(false);
    }
  };

  const getPriorityColor = (priorityName: string) => {
    const name = priorityName.toLowerCase();
    if (name.includes('high') || name.includes('urgent')) return 'destructive';
    if (name.includes('medium')) return 'default';
    return 'secondary';
  };

  const getPriorityIcon = (priorityName: string) => {
    const name = priorityName.toLowerCase();
    if (name.includes('high') || name.includes('urgent')) return <AlertCircle className="h-3 w-3" />;
    if (name.includes('medium')) return <Flag className="h-3 w-3" />;
    return <CheckCircle2 className="h-3 w-3" />;
  };

  const selectedTags = tags.filter((tag) => selectedTagIds.includes(tag.id));
  const availableTags = tags.filter((tag) => !selectedTagIds.includes(tag.id));

  return (
    <form onSubmit={handleSubmit} className="space-y-3 pt-4">
      <div className="space-y-2">
        <Label htmlFor="title" className="text-sm font-semibold text-gray-700">
          Task Title <span className="text-red-500">*</span>
        </Label>
        <Input
          type="text"
          id="title"
          placeholder="Enter task title..."
          className="h-11 text-base transition-all duration-200 focus:ring-2 focus:ring-cyan-500"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        {title && (
          <p className="text-xs text-gray-500">{title.length} characters</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="description" className="text-sm font-semibold text-gray-700">
          Description
        </Label>
        <textarea
          id="description"
          rows={3}
          placeholder="Add more details about this task..."
          className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200 resize-none"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        {description && (
          <p className="text-xs text-gray-500">{description.length} characters</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="priority" className="text-sm font-semibold text-gray-700 flex items-center gap-2">
            <Flag className="h-4 w-4" />
            Priority
          </Label>
          {isLoadingPriorities ? (
            <div className="h-11 rounded-md border border-input bg-muted animate-pulse" />
          ) : (
            <div className="space-y-2">
              {taskPriorities && taskPriorities.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {taskPriorities.map((p) => (
                    <Badge
                      key={p.id}
                      variant={priority === p.name ? getPriorityColor(p.name) : 'outline'}
                      className={`cursor-pointer transition-all duration-200 hover:scale-105 ${
                        priority === p.name ? 'ring-2 ring-offset-2 ring-cyan-500' : 'hover:bg-gray-100'
                      }`}
                      onClick={() => setPriority(p.name)}
                    >
                      {getPriorityIcon(p.name)}
                      {p.name}
                    </Badge>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No priorities available</p>
              )}
            </div>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="dueDate" className="text-sm font-semibold text-gray-700 flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            Due Date
          </Label>
          <Input
            type="date"
            id="dueDate"
            className="h-11 transition-all duration-200 focus:ring-2 focus:ring-cyan-500"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            min={new Date().toISOString().split('T')[0]}
          />
        </div>
      </div>

      <div className="space-y-3">
        <Label className="text-sm font-semibold text-gray-700 flex items-center gap-2">
          <Tags className="h-4 w-4" />
          Tags
          {selectedTagIds.length > 0 && (
            <span className="text-xs text-gray-500">({selectedTagIds.length} selected)</span>
          )}
        </Label>

        {isLoadingTags ? (
          <div className="h-16 rounded-md border border-input bg-muted animate-pulse" />
        ) : (
          <div className="space-y-3 p-4 rounded-lg border-2 border-dashed border-gray-200 bg-gray-50/50">
            {/* Selected Tags */}
            {selectedTags.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-medium text-gray-600 uppercase tracking-wide">Selected Tags</p>
                <div className="flex flex-wrap gap-2">
                  {selectedTags.map((tag) => (
                    <Badge
                      key={tag.id}
                      className="cursor-pointer transition-all duration-200 hover:scale-105 shadow-sm"
                      onClick={() => toggleTag(tag.id)}
                      style={{
                        backgroundColor: tag.color || '#6366f1',
                        color: 'white',
                        borderColor: tag.color || '#6366f1'
                      }}
                    >
                      <Sparkles className="h-3 w-3 mr-1" />
                      {tag.name}
                      <X className="ml-1 h-3 w-3" />
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Available Tags */}
            {availableTags.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-medium text-gray-600 uppercase tracking-wide">Available Tags</p>
                <div className="flex flex-wrap gap-2">
                  {availableTags.map((tag) => (
                    <Badge
                      key={tag.id}
                      variant="outline"
                      className="cursor-pointer transition-all duration-200 hover:scale-105 hover:shadow-md"
                      onClick={() => toggleTag(tag.id)}
                      style={{ borderColor: tag.color || undefined }}
                    >
                      {tag.name}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Create New Tag */}
            <div className="space-y-2 pt-3 border-t border-gray-200">
              <p className="text-xs font-medium text-gray-600 uppercase tracking-wide">Create New Tag</p>
              <div className="flex gap-2">
                <Input
                  type="text"
                  placeholder="Tag name..."
                  value={newTagName}
                  onChange={(e) => setNewTagName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleCreateTag();
                    }
                  }}
                  className="h-9 text-sm"
                  disabled={isCreatingTag}
                />
                <Button
                  type="button"
                  size="sm"
                  onClick={handleCreateTag}
                  disabled={!newTagName.trim() || isCreatingTag}
                  className="bg-cyan-500 hover:bg-cyan-600"
                >
                  {isCreatingTag ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <Plus className="h-4 w-4" />
                      Add
                    </>
                  )}
                </Button>
              </div>
            </div>

            {tags.length === 0 && !isCreatingTag && (
              <p className="text-sm text-gray-500 text-center py-2">No tags yet. Create one above!</p>
            )}
          </div>
        )}
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <Button
          type="submit"
          className="bg-gradient-to-r from-teal-500 to-cyan-600 hover:from-teal-600 hover:to-cyan-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105"
          size="lg"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Updating...
            </>
          ) : (
            <>
              <CheckCircle2 className="h-4 w-4" />
              Update Task
            </>
          )}
        </Button>
      </div>
    </form>
  );
};

export default EditTaskForm;
