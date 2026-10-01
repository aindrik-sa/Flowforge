import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { X } from 'lucide-react';
import { projectsApi } from '../api';
import { Input } from '@/shared/ui/Input';
import { Button } from '@/shared/ui/Button';
import './CreateProjectModal.css';

interface CreateProjectModalProps {
  workspaceId: string;
  isOpen: boolean;
  onClose: () => void;
}

export function CreateProjectModal({ workspaceId, isOpen, onClose }: CreateProjectModalProps) {
  const [name, setName] = useState('');
  const [key, setKey] = useState('');
  const [description, setDescription] = useState('');
  
  const queryClient = useQueryClient();

  useEffect(() => {
    // Auto-generate key from name if key hasn't been manually heavily edited
    if (name && key.length <= 3) {
      const words = name.split(' ');
      let generatedKey = '';
      if (words.length === 1) {
        generatedKey = name.substring(0, 3).toUpperCase();
      } else {
        generatedKey = words.map(w => w.charAt(0)).join('').substring(0, 3).toUpperCase();
      }
      setKey(generatedKey);
    }
  }, [name]);

  const createMutation = useMutation({
    mutationFn: (payload: any) => projectsApi.create(workspaceId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', workspaceId] });
      handleClose();
    }
  });

  const handleClose = () => {
    setName('');
    setKey('');
    setDescription('');
    onClose();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !key.trim()) return;
    
    createMutation.mutate({
      name,
      key: key.toUpperCase(),
      description
    });
  };

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop">
      <div className="modal-content glass">
        <button className="modal-close icon-btn" onClick={handleClose}>
          <X size={20} />
        </button>
        
        <h2 className="text-xl font-bold mb-1">Create Project</h2>
        <p className="text-secondary text-sm mb-6">Set up a new space for your team's work.</p>
        
        <form onSubmit={handleSubmit}>
          <div className="flex flex-col gap-4 mb-6">
            <div>
              <label className="text-sm font-medium text-secondary mb-1 block">Project Name</label>
              <Input 
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Website Redesign"
                required
                autoFocus
              />
            </div>
            
            <div>
              <label className="text-sm font-medium text-secondary mb-1 block">Project Key</label>
              <Input 
                value={key}
                onChange={(e) => setKey(e.target.value.toUpperCase())}
                placeholder="e.g. WEB"
                maxLength={5}
                required
              />
              <p className="text-xs text-tertiary mt-1">Used as a prefix for tasks (e.g. WEB-12)</p>
            </div>
            
            <div>
              <label className="text-sm font-medium text-secondary mb-1 block">Description</label>
              <textarea 
                className="input"
                style={{ minHeight: '80px', width: '100%', resize: 'none' }}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="What is this project about?"
              />
            </div>
          </div>
          
          <div className="flex justify-end gap-3">
            <Button variant="ghost" type="button" onClick={handleClose}>Cancel</Button>
            <Button variant="primary" type="submit" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Creating...' : 'Create Project'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
