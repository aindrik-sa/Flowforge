import React, { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import type { Project } from '../types';
import { Button } from '@/shared/ui/Button';
import { Input } from '@/shared/ui/Input';

export function ProjectSettingsPage() {
  const { project } = useOutletContext<{ project: Project }>();
  const [name, setName] = useState(project.name);
  
  return (
    <div className="max-w-3xl">
      <h2 className="text-xl font-bold mb-6">Project Details</h2>
      
      <div className="glass p-6 rounded-lg mb-8">
        <div className="flex flex-col gap-4 max-w-md">
          <div>
            <label className="text-sm font-medium text-secondary mb-1 block">Project Name</label>
            <Input 
              value={name} 
              onChange={e => setName(e.target.value)} 
            />
          </div>
          <div>
            <label className="text-sm font-medium text-secondary mb-1 block">Project Key</label>
            <Input 
              value={project.key} 
              disabled 
            />
            <p className="text-xs text-tertiary mt-1">The key cannot be changed after creation.</p>
          </div>
          <div className="pt-4">
            <Button variant="primary">Save Changes</Button>
          </div>
        </div>
      </div>
      
      <h2 className="text-xl font-bold text-error mb-4">Danger Zone</h2>
      <div className="border border-error/30 bg-error/5 p-6 rounded-lg">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="font-medium text-error mb-1">Archive Project</h3>
            <p className="text-sm text-secondary">Hide this project from the active list. It will become read-only.</p>
          </div>
          <Button variant="ghost" className="text-error border border-error/50 hover:bg-error hover:text-white">
            Archive Project
          </Button>
        </div>
      </div>
    </div>
  );
}
