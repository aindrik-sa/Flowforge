import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Plus } from 'lucide-react';
import { projectsApi } from '../api';
import { useCurrentWorkspace } from '../../workspaces/hooks/useCurrentWorkspace';
import { ProjectCard } from '../components/ProjectCard';
import { CreateProjectModal } from '../components/CreateProjectModal';
import { Button } from '@/shared/ui/Button';

export function ProjectsPage() {
  const { currentWorkspace, isLoading: isLoadingWorkspace } = useCurrentWorkspace();
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const { data: projects, isLoading: isLoadingProjects } = useQuery({
    queryKey: ['projects', currentWorkspace?.id],
    queryFn: () => projectsApi.list(currentWorkspace!.id),
    enabled: !!currentWorkspace,
  });

  if (isLoadingWorkspace || isLoadingProjects) {
    return <div className="text-secondary">Loading projects...</div>;
  }

  if (!currentWorkspace) {
    return <div className="text-secondary">No workspace found.</div>;
  }

  return (
    <div className="projects-page">
      <header className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-2xl font-bold mb-2">Projects</h1>
          <p className="text-secondary">Manage and track your active initiatives in {currentWorkspace.name}.</p>
        </div>
        
        <div className="flex gap-4">
          <div className="glass px-3 py-2 rounded flex items-center gap-2" style={{ width: '240px' }}>
            <Search size={16} className="text-secondary" />
            <input 
              type="text" 
              placeholder="Search projects..." 
              className="bg-transparent border-none outline-none text-sm w-full text-primary"
            />
          </div>
          <Button variant="primary" onClick={() => setIsModalOpen(true)}>
            <Plus size={16} />
            <span>New Project</span>
          </Button>
        </div>
      </header>
      
      <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '24px' }}>
        {projects?.map((project, i) => (
          <ProjectCard key={project.id} project={project} index={i} />
        ))}
      </div>
      
      {projects?.length === 0 && (
        <div className="flex flex-col items-center justify-center p-12 glass mt-8 rounded-lg text-center border-dashed">
          <div className="w-16 h-16 rounded-full bg-surface-2 flex items-center justify-center mb-4 text-accent">
            <Plus size={24} />
          </div>
          <h3 className="font-medium text-lg mb-2">No projects yet</h3>
          <p className="text-secondary mb-6 max-w-sm">Get started by creating your first project to track tasks, bugs, and features.</p>
          <Button variant="primary" onClick={() => setIsModalOpen(true)}>Create Project</Button>
        </div>
      )}

      {currentWorkspace && (
        <CreateProjectModal 
          workspaceId={currentWorkspace.id} 
          isOpen={isModalOpen} 
          onClose={() => setIsModalOpen(false)} 
        />
      )}
    </div>
  );
}
