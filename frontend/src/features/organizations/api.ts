import { apiClient } from '@/shared/lib/axios';
import type { Organization, OrganizationMember } from './types';

export const organizationsApi = {
  list: async (): Promise<Organization[]> => {
    const { data } = await apiClient.get('/organizations/');
    return data;
  },

  create: async (payload: { name: string; description?: string }): Promise<Organization> => {
    const { data } = await apiClient.post('/organizations/', payload);
    return data;
  },

  get: async (id: string): Promise<Organization> => {
    const { data } = await apiClient.get(`/organizations/${id}/`);
    return data;
  },

  getMembers: async (id: string): Promise<OrganizationMember[]> => {
    const { data } = await apiClient.get(`/organizations/${id}/members/`);
    return data;
  }
};
