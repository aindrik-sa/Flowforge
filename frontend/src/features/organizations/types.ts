export interface Organization {
  id: string;
  name: string;
  slug: string;
  description: string;
  created_at: string;
}

export interface OrganizationMember {
  id: string;
  organization: string;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  };
  role: 'owner' | 'admin' | 'manager' | 'member' | 'viewer';
  joined_at: string;
}
