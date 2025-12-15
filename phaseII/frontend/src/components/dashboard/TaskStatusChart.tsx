"use client";

import { Task } from '@/types';
import { CheckCircle2, Clock, Circle } from 'lucide-react';

interface TaskStatusChartProps {
  tasks: Task[];
}

interface CircularProgressProps {
  percentage: number;
  color: string;
  label: string;
  Icon: React.ComponentType<{ className?: string }>;
}

const CircularProgress = ({ percentage, color, label, Icon }: CircularProgressProps) => {
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-28 h-28">
        <svg className="w-full h-full transform -rotate-90">
          {/* Background circle */}
          <circle
            cx="56"
            cy="56"
            r="45"
            stroke="#E5E7EB"
            strokeWidth="8"
            fill="none"
          />
          {/* Progress circle */}
          <circle
            cx="56"
            cy="56"
            r="45"
            stroke={color}
            strokeWidth="8"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-500"
          />
        </svg>
        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div style={{ color }}>
            <Icon className="h-5 w-5 mb-1" />
          </div>
          <span className="text-lg font-bold text-gray-900">{percentage}%</span>
        </div>
      </div>
      <p className="text-sm text-gray-600 mt-2 text-center">{label}</p>
    </div>
  );
};

const TaskStatusChart = ({ tasks }: TaskStatusChartProps) => {
  const totalTasks = tasks.length;

  // Use actual status field for categorization
  const completed = tasks.filter(t => t.status === 'completed').length;
  const inProgress = tasks.filter(t => t.status === 'in_progress').length;
  const notStarted = tasks.filter(t => ['not_started', 'pending'].includes(t.status)).length;

  const completedPercentage = totalTasks > 0 ? Math.round((completed / totalTasks) * 100) : 0;
  const inProgressPercentage = totalTasks > 0 ? Math.round((inProgress / totalTasks) * 100) : 0;
  const notStartedPercentage = totalTasks > 0 ? Math.round((notStarted / totalTasks) * 100) : 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <div className="h-8 w-1 bg-coral rounded" />
        <h2 className="text-lg font-semibold text-gray-900">Task Status</h2>
      </div>

      <div className="flex justify-around items-start gap-4">
        <CircularProgress
          percentage={completedPercentage}
          color="#4CAF50"
          label="Completed"
          Icon={CheckCircle2}
        />
        <CircularProgress
          percentage={inProgressPercentage}
          color="#2196F3"
          label="In Progress"
          Icon={Clock}
        />
        <CircularProgress
          percentage={notStartedPercentage}
          color="#9E9E9E"
          label="Not Started"
          Icon={Circle}
        />
      </div>

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex justify-around text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-success" />
            <span className="text-gray-600">{completed} Completed</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-info" />
            <span className="text-gray-600">{inProgress} In Progress</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-gray-400" />
            <span className="text-gray-600">{notStarted} Not Started</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskStatusChart;
