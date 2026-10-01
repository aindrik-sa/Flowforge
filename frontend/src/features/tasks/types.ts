import type { Task } from '../board/types'; // reuse base Task type

export interface TaskActivityLog {
  id: string;
  action: 'created' | 'updated' | 'deleted';
  field_name: string;
  old_value: string;
  new_value: string;
  changed_by: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  };
  created_at: string;
}

export interface TaskUpdatePayload {
  title?: string;
  description?: string;
  priority?: string;
  due_date?: string | null;
  start_date?: string | null;
  estimated_hours?: number | null;
}
