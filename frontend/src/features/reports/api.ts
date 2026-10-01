import { apiClient } from '@/shared/lib/axios';
import type { ProjectDashboardStats, UserProductivityStats } from './types';

export const reportsApi = {
  getProjectDashboard: async (projectId: string): Promise<ProjectDashboardStats> => {
    const { data } = await apiClient.get(`/projects/${projectId}/dashboard/`);
    return data;
  },

  getUserProductivity: async (userId: string): Promise<UserProductivityStats> => {
    const { data } = await apiClient.get(`/users/${userId}/productivity/`);
    return data;
  }
};
