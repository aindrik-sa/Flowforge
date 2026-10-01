export interface Project {
  id: string;
  workspace: string;
  name: string;
  key: string;
  description: string;
  status: 'planned' | 'active' | 'on_hold' | 'completed' | 'archived';
  created_at: string;
}

export interface ProjectMember {
  id: string;
  project: string;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  };
  role: 'owner' | 'manager' | 'member' | 'viewer';
  joined_at: string;
}
