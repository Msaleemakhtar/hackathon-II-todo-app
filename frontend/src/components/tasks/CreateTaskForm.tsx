import React, { useState } from 'react';
import { useCategories } from '@/hooks/useCategories';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, Calendar, AlertCircle, Flag, Repeat, Bell } from 'lucide-react';
import { RecurrenceSelector, RecurrencePattern, patternToRRule } from './RecurrenceSelector';
import { ReminderSelector, ReminderConfig } from './ReminderSelector';

interface CreateTaskFormProps {
  onSubmit: (taskData: {
    title: string;
    description: string;
    priority: string;
    status: string;
    dueDate: string;
    recurrenceRule?: string | null;
    reminderConfig?: ReminderConfig | null;
  }) => void;
  isLoading?: boolean;
}

const CreateTaskForm = ({ onSubmit, isLoading }: CreateTaskFormProps) => {
  const { taskPriorities, taskStatuses, isLoadingPriorities, isLoadingStatuses } = useCategories();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('');
  const [status, setStatus] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [recurrencePattern, setRecurrencePattern] = useState<RecurrencePattern>({
    frequency: 'none',
    interval: 1,
    endType: 'never',
  });
  const [showRecurrence, setShowRecurrence] = useState(false);
  const [reminderConfig, setReminderConfig] = useState<ReminderConfig>({
    timing: 'none',
    channel: 'browser',
    message: '',
  });
  const [showReminder, setShowReminder] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Use the first priority if none selected and priorities are available
    const selectedPriority = priority || (taskPriorities && taskPriorities.length > 0 ? taskPriorities[0].name : 'medium');
    const selectedStatus = status || (taskStatuses && taskStatuses.length > 0 ? taskStatuses[0].name : 'not_started');

    // Convert recurrence pattern to RRULE string
    const recurrenceRule = patternToRRule(recurrencePattern, dueDate ? new Date(dueDate) : undefined);

    // Only include reminder config if timing is not 'none'
    const reminderData = reminderConfig.timing !== 'none' ? reminderConfig : null;

    await onSubmit({
      title,
      description,
      priority: selectedPriority,
      status: selectedStatus,
      dueDate,
      recurrenceRule,
      reminderConfig: reminderData,
    });

    // Reset form after successful submission
    setTitle('');
    setDescription('');
    setPriority('');
    setStatus('');
    setDueDate('');
    setRecurrencePattern({
      frequency: 'none',
      interval: 1,
      endType: 'never',
    });
    setShowRecurrence(false);
    setReminderConfig({
      timing: 'none',
      channel: 'browser',
      message: '',
    });
    setShowReminder(false);
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
          className="h-11 text-base transition-all duration-200 focus:ring-2 focus:ring-indigo-500"
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
          className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200 resize-none"
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
                        priority === p.name ? 'ring-2 ring-offset-2 ring-indigo-500' : 'hover:bg-gray-100'
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
          <Label htmlFor="status" className="text-sm font-semibold text-gray-700 flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            Status
          </Label>
          {isLoadingStatuses ? (
            <div className="h-11 rounded-md border border-input bg-muted animate-pulse" />
          ) : (
            <div className="space-y-2">
              {taskStatuses && taskStatuses.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {taskStatuses.map((s) => (
                    <Badge
                      key={s.id}
                      variant={status === s.name ? 'default' : 'outline'}
                      className={`cursor-pointer transition-all duration-200 hover:scale-105 ${
                        status === s.name ? 'ring-2 ring-offset-2 ring-indigo-500' : 'hover:bg-gray-100'
                      }`}
                      onClick={() => setStatus(s.name)}
                    >
                      {s.name}
                    </Badge>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No statuses available</p>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="dueDate" className="text-sm font-semibold text-gray-700 flex items-center gap-2">
          <Calendar className="h-4 w-4" />
          Due Date
        </Label>
        <Input
          type="date"
          id="dueDate"
          className="h-11 transition-all duration-200 focus:ring-2 focus:ring-indigo-500"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          min={new Date().toISOString().split('T')[0]}
        />
      </div>

      {/* Recurrence Section */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label className="text-sm font-semibold text-gray-700 flex items-center gap-2">
            <Repeat className="h-4 w-4" />
            Recurring Task
          </Label>
          <button
            type="button"
            onClick={() => setShowRecurrence(!showRecurrence)}
            className="text-sm text-indigo-600 hover:text-indigo-700 font-medium transition-colors"
          >
            {showRecurrence ? 'Hide' : 'Show'} Options
          </button>
        </div>

        {showRecurrence && (
          <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <RecurrenceSelector
              value={recurrencePattern}
              onChange={setRecurrencePattern}
            />
          </div>
        )}
      </div>

      {/* Reminder Section */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label className="text-sm font-semibold text-gray-700 flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Task Reminder
          </Label>
          <button
            type="button"
            onClick={() => setShowReminder(!showReminder)}
            className="text-sm text-indigo-600 hover:text-indigo-700 font-medium transition-colors"
          >
            {showReminder ? 'Hide' : 'Show'} Options
          </button>
        </div>

        {showReminder && (
          <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <ReminderSelector
              value={reminderConfig}
              onChange={setReminderConfig}
              dueDate={dueDate}
            />
          </div>
        )}
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <Button
          type="submit"
          className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105"
          size="lg"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Creating...
            </>
          ) : (
            <>
              <CheckCircle2 className="h-4 w-4" />
              Create Task
            </>
          )}
        </Button>
      </div>
    </form>
  );
};

export default CreateTaskForm;
