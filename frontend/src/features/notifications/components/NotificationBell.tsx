import React, { useState } from 'react';
import { Bell } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { notificationsApi } from '../api';
import { useRealtimeEvent } from '@/shared/hooks/useRealtimeEvent';
import './NotificationBell.css';

export function NotificationBell() {
  const [unreadCount, setUnreadCount] = useState(0);
  const [isRinging, setIsRinging] = useState(false);

  // Initial fetch
  useQuery({
    queryKey: ['notifications', 'unread'],
    queryFn: async () => {
      const data = await notificationsApi.getUnread();
      setUnreadCount(data.length);
      return data;
    },
  });

  // Listen to live events
  useRealtimeEvent('notification.created', () => {
    setUnreadCount(prev => prev + 1);
    setIsRinging(true);
    setTimeout(() => setIsRinging(false), 1000);
  });

  return (
    <button className="icon-btn relative bell-btn">
      <Bell size={20} className={isRinging ? 'ringing' : ''} />
      {unreadCount > 0 && (
        <span className={`unread-badge ${isRinging ? 'badge-pop' : ''}`}>
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}
    </button>
  );
}
