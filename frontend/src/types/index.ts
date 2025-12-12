export type Task = {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  priority: string; // Dynamic priority from categories
  status: string; // Task status: pending, in_progress, completed
  due_date: string | null;
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
