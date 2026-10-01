import React, { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { X, Clock } from 'lucide-react';
import { tasksApi } from '../api';
import { EditableField } from './EditableField';
import type { TaskUpdatePayload } from '../types';
import './TaskDetailDrawer.css';

export function TaskDetailDrawer() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const taskId = searchParams.get('task');
  const isOpen = !!taskId;

  const { data: task, isLoading } = useQuery({
    queryKey: ['task', taskId],
    queryFn: () => tasksApi.getTask(taskId!),
    enabled: isOpen,
  });

  const { data: activity } = useQuery({
    queryKey: ['task-activity', taskId],
    queryFn: () => tasksApi.getActivity(taskId!),
    enabled: isOpen,
  });

  const updateMutation = useMutation({
    mutationFn: (payload: TaskUpdatePayload) => tasksApi.updateTask(taskId!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['task', taskId] });
      queryClient.invalidateQueries({ queryKey: ['tasks'] }); // invalidate board tasks
      queryClient.invalidateQueries({ queryKey: ['task-activity', taskId] });
    }
  });

  const closeDrawer = () => {
    // Remove ?task= from URL
    const newParams = new URLSearchParams(searchParams);
    newParams.delete('task');
    navigate({ search: newParams.toString() }, { replace: true });
  };

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) closeDrawer();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <>
      <div className="drawer-backdrop" onClick={closeDrawer} />
      <div className={`drawer-container ${isOpen ? 'open' : ''}`}>
        <header className="drawer-header border-b border-[var(--border-subtle)] pb-4 mb-6">
          <div className="flex justify-between items-center mb-4">
            <span className="font-mono text-xs font-semibold text-secondary px-2 py-1 bg-surface-2 rounded">
              {task?.key || 'Loading...'}
            </span>
            <button className="icon-btn" onClick={closeDrawer}>
              <X size={20} />
            </button>
          </div>
          
          {isLoading ? (
            <div className="h-8 bg-surface-glass rounded animate-pulse w-3/4"></div>
          ) : task ? (
            <EditableField 
              value={task.title} 
              onSave={(val) => updateMutation.mutate({ title: val })}
              className="text-2xl font-bold"
            />
          ) : null}
        </header>

        {isLoading ? (
          <div className="p-4 text-secondary">Loading details...</div>
        ) : task ? (
          <div className="drawer-body">
            <div className="main-content">
              <div className="mb-8">
                <h3 className="text-sm font-medium text-secondary mb-2">Description</h3>
                <EditableField 
                  type="textarea"
                  value={task.description} 
                  onSave={(val) => updateMutation.mutate({ description: val })}
                  placeholder="Add a more detailed description..."
                  className="text-[15px]"
                />
              </div>

              <div className="mb-8">
                <h3 className="text-sm font-medium text-secondary mb-4 flex items-center gap-2">
                  <Clock size={16} /> Activity
                </h3>
                <div className="activity-timeline">
                  {activity?.map(log => (
                    <div key={log.id} className="activity-item">
                      <div className="activity-avatar">
                        {log.changed_by.first_name?.[0] || 'U'}
                      </div>
                      <div className="activity-content">
                        <span className="font-medium text-primary">
                          {log.changed_by.first_name} {log.changed_by.last_name}
                        </span>{' '}
                        <span className="text-secondary">
                          {log.action} {log.field_name ? `the ${log.field_name}` : 'the task'}
                        </span>
                        <div className="text-xs text-tertiary mt-1">
                          {new Date(log.created_at).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                  {activity?.length === 0 && (
                    <div className="text-sm text-tertiary italic">No activity yet.</div>
                  )}
                </div>
              </div>
            </div>

            <div className="sidebar-content">
              <div className="property-grid">
                <div className="property-row">
                  <div className="property-label">Status</div>
                  <div className="property-value capitalize">
                    {/* Simplified for now, just shows column name roughly or status placeholder */}
                    In Progress
                  </div>
                </div>
                <div className="property-row">
                  <div className="property-label">Priority</div>
                  <div className="property-value">
                    <select 
                      className="bg-transparent text-primary outline-none cursor-pointer"
                      value={task.priority}
                      onChange={(e) => updateMutation.mutate({ priority: e.target.value })}
                    >
                      <option value="lowest">Lowest</option>
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="highest">Highest</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                </div>
                <div className="property-row">
                  <div className="property-label">Assignee</div>
                  <div className="property-value text-secondary">
                    Unassigned
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </>
  );
}
