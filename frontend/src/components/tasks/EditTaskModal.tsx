import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Edit3 } from "lucide-react";
import EditTaskForm from "./EditTaskForm";
import { Task } from '@/types';

interface EditTaskModalProps {
  task: Task | null;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (taskData: { title: string; description: string; priority: string; dueDate: string; tagIds: number[] }) => void;
}

const EditTaskModal = ({ task, isOpen, onOpenChange, onSubmit }: EditTaskModalProps) => {
  if (!task) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[85vh] overflow-hidden p-0 flex flex-col">
        <div className="bg-gradient-to-r from-teal-500 via-cyan-500 to-blue-500 p-4">
          <DialogHeader className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="rounded-full bg-white/20 backdrop-blur-sm p-1.5">
                <Edit3 className="h-4 w-4 text-white" />
              </div>
              <DialogTitle className="text-xl font-bold text-white">Edit Task</DialogTitle>
            </div>
            <DialogDescription className="text-cyan-50 text-sm">
              Update your task details, tags, and priority
            </DialogDescription>
          </DialogHeader>
        </div>
        <div className="p-4 pt-0 -mt-2 bg-white rounded-t-2xl overflow-y-auto flex-1">
          <EditTaskForm task={task} onSubmit={onSubmit} />
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default EditTaskModal;
