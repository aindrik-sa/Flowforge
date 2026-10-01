import React, { useMemo } from 'react';
import { useOutletContext } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { DragDropContext, Droppable, DropResult } from '@hello-pangea/dnd';
import { boardApi } from '../api';
import type { Project } from '../../projects/types';
import type { Task, BoardColumn } from '../types';
import { BoardColumnComponent } from '../components/BoardColumn';
import './BoardPage.css';

export function BoardPage() {
  const { project } = useOutletContext<{ project: Project }>();
  const queryClient = useQueryClient();

  const { data: boards } = useQuery({
    queryKey: ['boards', project.id],
    queryFn: () => boardApi.getBoards(project.id),
  });
  const board = boards?.[0];

  const { data: columns } = useQuery({
    queryKey: ['columns', board?.id],
    queryFn: () => boardApi.getColumns(board!.id),
    enabled: !!board,
  });

  const { data: tasks, isLoading: loadingTasks } = useQuery({
    queryKey: ['tasks', project.id],
    queryFn: () => boardApi.getTasks(project.id),
  });

  const tasksByColumn = useMemo(() => {
    if (!tasks) return {};
    const grouped: Record<string, Task[]> = {};
    columns?.forEach(c => grouped[c.id] = []); // ensure all columns exist
    tasks.forEach(task => {
      if (!grouped[task.column]) grouped[task.column] = [];
      grouped[task.column].push({ ...task });
    });
    Object.values(grouped).forEach(list => list.sort((a, b) => a.position - b.position));
    return grouped;
  }, [tasks, columns]);

  const moveTaskMutation = useMutation({
    mutationFn: (vars: { taskId: string; column_id: string; position: number }) => 
      boardApi.moveTask(vars.taskId, { column_id: vars.column_id, position: vars.position }),
    onMutate: async (vars) => {
      await queryClient.cancelQueries({ queryKey: ['tasks', project.id] });
      const previousTasks = queryClient.getQueryData<Task[]>(['tasks', project.id]);
      
      queryClient.setQueryData(['tasks', project.id], (old: Task[] | undefined) => {
        if (!old) return old;
        const allTasks = old.map(t => ({ ...t }));
        const taskIndex = allTasks.findIndex(t => t.id === vars.taskId);
        if (taskIndex === -1) return old;
        
        const taskToMove = allTasks[taskIndex];
        const oldColId = taskToMove.column;
        
        // Remove from old
        const oldColTasks = allTasks.filter(t => t.column === oldColId && t.id !== taskToMove.id).sort((a,b) => a.position - b.position);
        oldColTasks.forEach((t, i) => t.position = i);
        
        // Target col handling
        let targetColTasks = allTasks.filter(t => t.column === vars.column_id && t.id !== taskToMove.id).sort((a,b) => a.position - b.position);
        
        taskToMove.column = vars.column_id;
        taskToMove.position = vars.position;
        targetColTasks.splice(vars.position, 0, taskToMove);
        targetColTasks.forEach((t, i) => t.position = i);
        
        const untouchedTasks = allTasks.filter(t => t.column !== oldColId && t.column !== vars.column_id);
        
        if (oldColId === vars.column_id) {
          return [...untouchedTasks, ...targetColTasks];
        } else {
          return [...untouchedTasks, ...oldColTasks, ...targetColTasks];
        }
      });
      return { previousTasks };
    },
    onError: (err, newTodo, context) => {
      queryClient.setQueryData(['tasks', project.id], context?.previousTasks);
      console.error('Failed to move task:', err);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', project.id] });
    }
  });

  const reorderColumnsMutation = useMutation({
    mutationFn: (vars: { boardId: string; ordered_column_ids: string[] }) =>
      boardApi.reorderColumns(vars.boardId, { ordered_column_ids: vars.ordered_column_ids }),
    onMutate: async (vars) => {
      await queryClient.cancelQueries({ queryKey: ['columns', board?.id] });
      const previousColumns = queryClient.getQueryData<BoardColumn[]>(['columns', board?.id]);
      
      queryClient.setQueryData(['columns', board?.id], (old: BoardColumn[] | undefined) => {
        if (!old) return old;
        const newCols = [...old];
        const oldIndex = previousColumns?.findIndex(c => c.id === resultDrag.draggableId) || 0;
        // The actual logic is simple since we have ordered IDs, we can just sort old array by index in ordered_column_ids
        return newCols.sort((a, b) => vars.ordered_column_ids.indexOf(a.id) - vars.ordered_column_ids.indexOf(b.id));
      });
      return { previousColumns };
    },
    onError: (err, vars, context) => {
      queryClient.setQueryData(['columns', board?.id], context?.previousColumns);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['columns', board?.id] });
    }
  });

  // Hacky ref to pass draggableId to onMutate
  let resultDrag: any = null;

  const onDragEnd = (result: DropResult) => {
    resultDrag = result;
    const { destination, source, draggableId, type } = result;

    if (!destination) return;
    if (destination.droppableId === source.droppableId && destination.index === source.index) return;

    if (type === 'TASK') {
      moveTaskMutation.mutate({
        taskId: draggableId,
        column_id: destination.droppableId,
        position: destination.index
      });
    } else if (type === 'COLUMN' && board) {
      if (!columns) return;
      const newColumnOrder = Array.from(columns.map(c => c.id));
      newColumnOrder.splice(source.index, 1);
      newColumnOrder.splice(destination.index, 0, draggableId.replace('column-', ''));
      
      reorderColumnsMutation.mutate({
        boardId: board.id,
        ordered_column_ids: newColumnOrder
      });
    }
  };

  if (loadingTasks) return <div className="p-8 text-secondary">Loading board...</div>;
  if (!board) return <div className="p-8 text-secondary">No board found.</div>;

  return (
    <div className="board-page">
      <div className="board-toolbar mb-6 flex justify-between">
        <div className="flex gap-2">
          <div className="glass px-3 py-1.5 rounded text-sm text-secondary">All Assignees</div>
          <div className="glass px-3 py-1.5 rounded text-sm text-secondary">Any Priority</div>
        </div>
      </div>

      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="board" direction="horizontal" type="COLUMN">
          {(provided) => (
            <div 
              className="board-canvas"
              ref={provided.innerRef}
              {...provided.droppableProps}
            >
              {columns?.map((col, index) => (
                <BoardColumnComponent 
                  key={col.id} 
                  column={col} 
                  tasks={tasksByColumn[col.id] || []} 
                  projectId={project.id}
                  index={index}
                />
              ))}
              {provided.placeholder}
              
              <button className="add-column-btn glass shrink-0">
                + Add Column
              </button>
            </div>
          )}
        </Droppable>
      </DragDropContext>
    </div>
  );
}
