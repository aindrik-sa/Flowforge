import React from 'react';
import { useSearchParams } from 'react-router-dom';
import { Draggable } from '@hello-pangea/dnd';
import { AlertCircle, ArrowDown, ArrowUp, ChevronDown, ChevronUp } from 'lucide-react';
import type { Task } from '../types';
import './TaskCard.css';

interface TaskCardProps {
  task: Task;
  index: number;
}

const priorityConfig: Record<string, { icon: React.ReactNode, color: string }> = {
  lowest: { icon: <ChevronDown size={14} />, color: '#6b7280' },
  low: { icon: <ArrowDown size={14} />, color: '#3b82f6' },
  medium: { icon: <div className="w-3 h-1 bg-current rounded-full" />, color: '#f59e0b' },
  high: { icon: <ArrowUp size={14} />, color: '#ef4444' },
  highest: { icon: <ChevronUp size={14} />, color: '#dc2626' },
  critical: { icon: <AlertCircle size={14} />, color: '#991b1b' },
};

export const TaskCard = React.memo(({ task, index }: TaskCardProps) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const prio = priorityConfig[task.priority] || priorityConfig.medium;

  const handleClick = () => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('task', task.id);
    setSearchParams(newParams);
  };

  return (
    <Draggable draggableId={task.id} index={index}>
      {(provided, snapshot) => (
        <div 
          className={`task-card ${snapshot.isDragging ? 'is-dragging' : ''}`}
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          onClick={handleClick}
        >
          <div className="task-title">{task.title}</div>
          <div className="task-meta">
            <span className="task-key text-xs font-mono text-secondary">{task.key}</span>
            <div className="flex items-center gap-2">
              <div className="priority-icon flex items-center justify-center" style={{ color: prio.color }} title={task.priority}>
                {prio.icon}
              </div>
              <div className="w-5 h-5 rounded-full bg-surface-3 flex flex-shrink-0 items-center justify-center text-[10px] text-white">
                U
              </div>
            </div>
          </div>
        </div>
      )}
    </Draggable>
  );
});
