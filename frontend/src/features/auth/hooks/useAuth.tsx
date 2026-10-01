import React, { createContext, useContext, useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { User, AuthResponse } from '../types';
import { authApi } from '../api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (credentials: Record<string, string>) => Promise<void>;
  register: (credentials: Record<string, string>) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));

  // Automatically fetch user if we have a token
  const { data: user, isLoading, isError } = useQuery({
    queryKey: ['me'],
    queryFn: authApi.me,
    enabled: !!token,
    retry: false,
  });

  // If fetching 'me' fails (e.g. token completely invalid/expired and refresh failed), log out
  useEffect(() => {
    if (isError) {
      logout();
    }
  }, [isError]);

  const loginMutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: (data: AuthResponse) => {
      handleAuthSuccess(data);
    },
  });

  const registerMutation = useMutation({
    mutationFn: authApi.register,
    onSuccess: (data: AuthResponse) => {
      handleAuthSuccess(data);
    },
  });

  const handleAuthSuccess = (data: AuthResponse) => {
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    setToken(data.access);
    queryClient.setQueryData(['me'], data.user);
  };

  const login = async (credentials: Record<string, string>) => {
    await loginMutation.mutateAsync(credentials);
  };

  const register = async (credentials: Record<string, string>) => {
    await registerMutation.mutateAsync(credentials);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setToken(null);
    queryClient.setQueryData(['me'], null);
    queryClient.clear();
  };

  const contextValue = {
    user: user ?? null,
    isLoading: isLoading || loginMutation.isPending || registerMutation.isPending,
    login,
    register,
    logout,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
