import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import CreateTaskForm from "./CreateTaskForm";

interface CreateTaskModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (taskData: { title: string; description: string; priority: 'low' | 'medium' | 'high'; dueDate: string }) => void;
}

const CreateTaskModal = ({ isOpen, onOpenChange, onSubmit }: CreateTaskModalProps) => {
  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create New Task</DialogTitle>
          <DialogDescription>
            Fill in the details below to create a new task.
          </DialogDescription>
        </DialogHeader>
        <CreateTaskForm onSubmit={onSubmit} />
      </DialogContent>
    </Dialog>
  );
};

export default CreateTaskModal;
