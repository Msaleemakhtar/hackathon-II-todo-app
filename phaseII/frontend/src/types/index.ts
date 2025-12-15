export type Task = {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  priority: string; // Dynamic priority from categories
  status: string; // Task status: pending, in_progress, completed
  due_date: string | null;
  recurrence_rule: string | null; // iCal RRULE string
  parent_task_id: number | null; // Parent task ID for recurring instances
  is_recurring_instance: boolean; // Whether this is an instance of a recurring task
  occurrence_date: string | null; // Specific occurrence date for instances
  created_at: string;
  updated_at: string;
  tags: Tag[];
};

export type Tag = {
  id: number;
  name: string;
  color: string | null;
};

export type UserProfile = {
  id: string;
  email: string;
  name: string | null;
};
