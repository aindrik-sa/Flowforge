import { apiClient } from '@/shared/lib/axios';
import type { Workspace } from './types';

export const workspacesApi = {
  list: async (orgId: string): Promise<Workspace[]> => {
    const { data } = await apiClient.get(`/organizations/${orgId}/workspaces/`);
    return data;
  },

  create: async (orgId: string, payload: { name: string; description?: string }): Promise<Workspace> => {
    const { data } = await apiClient.post(`/organizations/${orgId}/workspaces/`, payload);
    return data;
  },

  get: async (id: string): Promise<Workspace> => {
    const { data } = await apiClient.get(`/workspaces/${id}/`);
    return data;
  }
};
