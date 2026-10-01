export interface Board {
  id: string;
  project: string;
  name: string;
  is_default: boolean;
}

export interface BoardColumn {
  id: string;
  board: string;
  name: string;
  position: number;
}

export interface Task {
  id: string;
  project: string;
  column: string;
  title: string;
  key: string;
  description: string;
  priority: 'lowest' | 'low' | 'medium' | 'high' | 'highest' | 'critical';
  position: number;
  created_at: string;
}

// Minimal types for assignees/labels
export interface TaskAssignment {
  id: string;
  user: { id: string; first_name: string; last_name: string; email: string };
}
