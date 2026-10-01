import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { MoreHorizontal, Plus } from 'lucide-react';
import { Draggable, Droppable } from '@hello-pangea/dnd';
import type { BoardColumn, Task } from '../types';
import { TaskCard } from './TaskCard';
import { boardApi } from '../api';
import './BoardColumn.css';

interface BoardColumnProps {
  column: BoardColumn;
  tasks: Task[];
  projectId: string;
  index: number;
}

export function BoardColumnComponent({ column, tasks, projectId, index }: BoardColumnProps) {
  const [isAdding, setIsAdding] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: (title: string) => boardApi.createTask(projectId, { 
      title, 
      column: column.id,
      priority: 'medium'
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
      setNewTaskTitle('');
      setIsAdding(false);
    }
  });

  const handleQuickAdd = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && newTaskTitle.trim()) {
      createMutation.mutate(newTaskTitle);
    } else if (e.key === 'Escape') {
      setIsAdding(false);
      setNewTaskTitle('');
    }
  };

  return (
    <Draggable draggableId={`column-${column.id}`} index={index}>
      {(provided, snapshot) => (
        <div 
          className={`board-column glass ${snapshot.isDragging ? 'is-dragging' : ''}`}
          ref={provided.innerRef}
          {...provided.draggableProps}
        >
          <div className="column-header" {...provided.dragHandleProps}>
            <div className="flex items-center gap-2">
              <div className="status-dot"></div>
              <h3 className="font-semibold">{column.name}</h3>
              <span className="task-count">{tasks.length}</span>
            </div>
            <button className="icon-btn text-secondary">
              <MoreHorizontal size={16} />
            </button>
          </div>

          <Droppable droppableId={column.id} type="TASK">
            {(providedDrop, snapshotDrop) => (
              <div 
                className={`column-tasks ${snapshotDrop.isDraggingOver ? 'dragging-over' : ''}`}
                ref={providedDrop.innerRef}
                {...providedDrop.droppableProps}
              >
                {tasks.map((task, i) => (
                  <TaskCard key={task.id} task={task} index={i} />
                ))}
                {providedDrop.placeholder}
                
                {isAdding ? (
                  <div className="quick-add-input-wrapper">
                    <input
                      type="text"
                      autoFocus
                      className="quick-add-input glass"
                      placeholder="What needs to be done?"
                      value={newTaskTitle}
                      onChange={(e) => setNewTaskTitle(e.target.value)}
                      onKeyDown={handleQuickAdd}
                      onBlur={() => setIsAdding(false)}
                      disabled={createMutation.isPending}
                    />
                  </div>
                ) : (
                  <button className="quick-add-btn mt-auto" onClick={() => setIsAdding(true)}>
                    <Plus size={16} />
                    <span>Add task</span>
                  </button>
                )}
              </div>
            )}
          </Droppable>
        </div>
      )}
    </Draggable>
  );
}
