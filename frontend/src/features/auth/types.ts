export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  created_at?: string;
  updated_at?: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  user: User;
  access: string;
  refresh: string;
}

export interface ApiError {
  detail?: string;
  [key: string]: string[] | string | undefined;
}
