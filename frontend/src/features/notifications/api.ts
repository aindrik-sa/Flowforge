import { apiClient } from '@/shared/lib/axios';
import type { Notification } from './types';

export const notificationsApi = {
  getUnread: async (): Promise<Notification[]> => {
    // Return empty list as mock since we don't have the endpoint implemented fully in the backend docs context,
    // but we will try the backend endpoint if it exists.
    try {
      const { data } = await apiClient.get('/notifications/?is_read=false');
      return data.results || data;
    } catch {
      return [];
    }
  },

  markAsRead: async (id: string): Promise<void> => {
    await apiClient.patch(`/notifications/${id}/read/`);
  },

  markAllAsRead: async (): Promise<void> => {
    await apiClient.post('/notifications/mark-all-read/');
  }
};
