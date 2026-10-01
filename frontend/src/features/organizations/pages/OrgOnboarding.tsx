import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { organizationsApi } from '../api';
import { Input } from '@/shared/ui/Input';
import { Button } from '@/shared/ui/Button';

export function OrgOnboarding() {
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: organizationsApi.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
      navigate(`/${data.id}`);
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to create organization.');
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!name.trim()) return;
    createMutation.mutate({ name });
  };

  return (
    <div className="flex items-center justify-center" style={{ minHeight: '100vh', backgroundColor: 'var(--bg-0)' }}>
      <div className="glass" style={{ width: '100%', maxWidth: '440px', padding: '40px', borderRadius: 'var(--radius-lg)' }}>
        <h2 style={{ marginBottom: '8px' }}>Create an Organization</h2>
        <p className="text-secondary" style={{ marginBottom: '32px' }}>
          FlowForge organizes everything within a top-level organization. Let's create yours.
        </p>
        
        <form onSubmit={handleSubmit}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '24px' }}>
            <label className="text-sm font-medium text-secondary">Organization Name</label>
            <Input 
              placeholder="e.g. Acme Corp" 
              value={name} 
              onChange={e => setName(e.target.value)} 
              required
              autoFocus
            />
          </div>
          
          {error && <div className="text-sm" style={{ color: 'var(--status-urgent)', marginBottom: '16px' }}>{error}</div>}
          
          <Button type="submit" variant="primary" style={{ width: '100%' }} disabled={createMutation.isPending}>
            {createMutation.isPending ? 'Creating...' : 'Create Organization'}
          </Button>
        </form>
      </div>
    </div>
  );
}
