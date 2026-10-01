import { apiClient } from '@/shared/lib/axios';
import type { TaskActivityLog, TaskUpdatePayload } from './types';
import type { Task, TaskAssignment } from '../board/types';

export const tasksApi = {
  getTask: async (taskId: string): Promise<Task> => {
    const { data } = await apiClient.get(`/tasks/${taskId}/`);
    return data;
  },

  updateTask: async (taskId: string, payload: TaskUpdatePayload): Promise<Task> => {
    const { data } = await apiClient.patch(`/tasks/${taskId}/`, payload);
    return data;
  },

  getActivity: async (taskId: string): Promise<TaskActivityLog[]> => {
    const { data } = await apiClient.get(`/tasks/${taskId}/activity/`);
    return data;
  },

  getAssignees: async (taskId: string): Promise<TaskAssignment[]> => {
    const { data } = await apiClient.get(`/tasks/${taskId}/assignees/`);
    return data;
  }
};
