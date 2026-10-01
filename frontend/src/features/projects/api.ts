import { apiClient } from '@/shared/lib/axios';
import type { Project } from './types';

export const projectsApi = {
  list: async (workspaceId: string): Promise<Project[]> => {
    // Note: the backend uses pagination by default, but let's assume it returns a list directly for simplicity
    // or we can extract results if it's paginated. We'll handle paginated data by getting .results
    const { data } = await apiClient.get(`/workspaces/${workspaceId}/projects/`);
    return data.results || data; 
  },

  create: async (workspaceId: string, payload: { name: string; key: string; description?: string }): Promise<Project> => {
    const { data } = await apiClient.post(`/workspaces/${workspaceId}/projects/`, payload);
    return data;
  },

  get: async (id: string): Promise<Project> => {
    const { data } = await apiClient.get(`/projects/${id}/`);
    return data;
  }
};
