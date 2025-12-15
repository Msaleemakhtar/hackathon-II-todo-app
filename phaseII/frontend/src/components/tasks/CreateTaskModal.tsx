import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { PlusCircle } from "lucide-react";
import CreateTaskForm from "./CreateTaskForm";

interface CreateTaskModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (taskData: { title: string; description: string; priority: string; status: string; dueDate: string }) => void;
  isLoading?: boolean;
}

const CreateTaskModal = ({ isOpen, onOpenChange, onSubmit, isLoading }: CreateTaskModalProps) => {
  // Prevent closing modal while loading
  const handleOpenChange = (open: boolean) => {
    if (!isLoading) {
      onOpenChange(open);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[550px] max-h-[85vh] overflow-hidden p-0 flex flex-col">
        <div className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 p-4">
          <DialogHeader className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="rounded-full bg-white/20 backdrop-blur-sm p-1.5">
                <PlusCircle className="h-4 w-4 text-white" />
              </div>
              <DialogTitle className="text-xl font-bold text-white">Create New Task</DialogTitle>
            </div>
            <DialogDescription className="text-indigo-50 text-sm">
              Fill in the details to create a new task
            </DialogDescription>
          </DialogHeader>
        </div>
        <div className="p-4 pt-0 -mt-2 bg-white rounded-t-2xl overflow-y-auto flex-1">
          <CreateTaskForm onSubmit={onSubmit} isLoading={isLoading} />
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default CreateTaskModal;
