export interface Notification {
  id: string;
  recipient: string;
  actor: {
    id: string;
    first_name: string;
    last_name: string;
  };
  verb: string;
  target_type: string;
  target_id: string;
  target_name: string;
  is_read: boolean;
  created_at: string;
}

export type RealtimeEventType = 'notification.created' | 'task.updated' | 'task.moved' | 'comment.created';

export interface RealtimeEvent {
  type: RealtimeEventType;
  payload: any;
}
