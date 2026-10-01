import { apiClient } from '@/shared/lib/axios';
import type { AuthResponse, AuthTokens, User } from './types';

export const authApi = {
  login: async (credentials: Record<string, string>): Promise<AuthResponse> => {
    const { data } = await apiClient.post('/auth/login/', credentials);
    return data;
  },

  register: async (credentials: Record<string, string>): Promise<AuthResponse> => {
    const { data } = await apiClient.post('/auth/register/', credentials);
    return data;
  },

  refresh: async (refresh: string): Promise<AuthTokens> => {
    const { data } = await apiClient.post('/auth/refresh/', { refresh });
    return data;
  },

  me: async (): Promise<User> => {
    const { data } = await apiClient.get('/auth/me/');
    return data;
  }
};
