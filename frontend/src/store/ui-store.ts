import { create } from 'zustand';
import { Task, Tag, UserProfile } from '@/types';

type TaskDisplay = Task & {
  ui_status: 'Not Started' | 'In Progress' | 'Completed';
  is_loading: boolean;
};

type UIState = {
  tasks: TaskDisplay[];
  tags: Tag[];
  userProfile: UserProfile | null;
  isLoadingTasks: boolean;
  error: string | null;
  searchTerm: string;
  filters: {
    status: string | null;
    priority: string | null;
    tags: string[];
  };
  sort: {
    key: string;
    direction: 'asc' | 'desc';
  };
  isCreateTaskModalOpen: boolean;
  editingTaskId: number | null;
  taskStats: {
    completed: number;
    inProgress: number;
    notStarted: number;
  };
};

type UIActions = {
  setTasks: (tasks: TaskDisplay[]) => void;
  setTags: (tags: Tag[]) => void;
  setUserProfile: (userProfile: UserProfile | null) => void;
  setIsLoadingTasks: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  setSearchTerm: (searchTerm: string) => void;
  setFilters: (filters: UIState['filters']) => void;
  setSort: (sort: UIState['sort']) => void;
  setIsCreateTaskModalOpen: (isOpen: boolean) => void;
  setEditingTaskId: (id: number | null) => void;
  setTaskStats: (stats: UIState['taskStats']) => void;
};

export const useUIStore = create<UIState & UIActions>((set) => ({
  tasks: [],
  tags: [],
  userProfile: null,
  isLoadingTasks: false,
  error: null,
  searchTerm: '',
  filters: {
    status: null,
    priority: null,
    tags: [],
  },
  sort: {
    key: 'created_at',
    direction: 'desc',
  },
  isCreateTaskModalOpen: false,
  editingTaskId: null,
  taskStats: {
    completed: 0,
    inProgress: 0,
    notStarted: 0,
  },
  setTasks: (tasks) => set({ tasks }),
  setTags: (tags) => set({ tags }),
  setUserProfile: (userProfile) => set({ userProfile }),
  setIsLoadingTasks: (isLoading) => set({ isLoadingTasks: isLoading }),
  setError: (error) => set({ error }),
  setSearchTerm: (searchTerm) => set({ searchTerm }),
  setFilters: (filters) => set({ filters }),
  setSort: (sort) => set({ sort }),
  setIsCreateTaskModalOpen: (isOpen) => set({ isCreateTaskModalOpen: isOpen }),
  setEditingTaskId: (id) => set({ editingTaskId: id }),
  setTaskStats: (stats) => set({ taskStats: stats }),
}));
