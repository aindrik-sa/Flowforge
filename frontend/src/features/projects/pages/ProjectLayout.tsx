import React from 'react';
import { Outlet, NavLink, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { projectsApi } from '../api';
import { TaskDetailDrawer } from '../../tasks/components/TaskDetailDrawer';
import './ProjectLayout.css';

export function ProjectLayout() {
  const { projectId } = useParams<{ projectId: string }>();

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.get(projectId!),
    enabled: !!projectId,
  });

  if (isLoading) {
    return <div className="text-secondary p-8">Loading project...</div>;
  }

  if (!project) {
    return <div className="text-secondary p-8">Project not found.</div>;
  }

  return (
    <div className="project-layout">
      <header className="project-header mb-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center font-bold text-white shadow-lg">
            {project.key.substring(0, 2)}
          </div>
          <div>
            <h1 className="text-2xl font-bold">{project.name}</h1>
            <p className="text-secondary text-sm">{project.key} • {project.status.replace('_', ' ')}</p>
          </div>
        </div>
        
        <nav className="project-tabs border-b border-[var(--border-subtle)] flex gap-6">
          <NavLink to="board" className={({ isActive }) => `tab-item ${isActive ? 'active' : ''}`}>
            Board
          </NavLink>
          <NavLink to="list" className={({ isActive }) => `tab-item ${isActive ? 'active' : ''}`}>
            List
          </NavLink>
          <NavLink to="reports" className={({ isActive }) => `tab-item ${isActive ? 'active' : ''}`}>
            Reports
          </NavLink>
          <NavLink to="settings" className={({ isActive }) => `tab-item ${isActive ? 'active' : ''}`}>
            Settings
          </NavLink>
        </nav>
      </header>
      
      <main className="project-content">
        <Outlet context={{ project }} />
      </main>
      
      <TaskDetailDrawer />
    </div>
  );
}
