import { apiClient } from '@/shared/lib/axios';
import type { Board, BoardColumn, Task } from './types';

export const boardApi = {
  getBoards: async (projectId: string): Promise<Board[]> => {
    const { data } = await apiClient.get(`/projects/${projectId}/boards/`);
    return data.results || data;
  },

  getColumns: async (boardId: string): Promise<BoardColumn[]> => {
    const { data } = await apiClient.get(`/boards/${boardId}/columns/`);
    // Assuming API returns results sorted by position, but let's ensure it here just in case
    const columns = data.results || data;
    return columns.sort((a: BoardColumn, b: BoardColumn) => a.position - b.position);
  },

  getTasks: async (projectId: string): Promise<Task[]> => {
    const { data } = await apiClient.get(`/projects/${projectId}/tasks/`);
    return data.results || data;
  },

  createTask: async (projectId: string, payload: { title: string; column: string; priority?: string }): Promise<Task> => {
    const { data } = await apiClient.post(`/projects/${projectId}/tasks/`, payload);
    return data;
  },

  moveTask: async (taskId: string, payload: { column_id: string; position: number }): Promise<Task> => {
    const { data } = await apiClient.post(`/tasks/${taskId}/move/`, payload);
    return data;
  },

  reorderColumns: async (boardId: string, payload: { ordered_column_ids: string[] }): Promise<BoardColumn[]> => {
    const { data } = await apiClient.post(`/boards/${boardId}/columns/reorder/`, payload);
    return data;
  }
};
