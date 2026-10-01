import React from 'react';
import { Outlet, Navigate, useParams } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { useCurrentOrg } from '../features/organizations/hooks/useCurrentOrg';
import { NotificationBell } from '../features/notifications/components/NotificationBell';
import { CommandPalette } from './CommandPalette';
import './AppShell.css';

export function AppShell() {
  const { currentOrg, isLoading } = useCurrentOrg();
  const { orgId } = useParams<{ orgId: string }>();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center" style={{ height: '100vh' }}>
        <p className="text-secondary">Loading your workspace...</p>
      </div>
    );
  }

  // Redirect to create org if they have none
  if (!currentOrg) {
    return <Navigate to="/onboarding" replace />;
  }

  // If no orgId in URL but we have a default org, redirect to it
  if (!orgId && currentOrg) {
    return <Navigate to={`/${currentOrg.id}`} replace />;
  }

  return (
    <div className="app-shell">
      <Sidebar currentOrg={currentOrg} />
      <div className="app-main">
        <header className="app-topbar glass flex justify-between items-center">
          <div className="breadcrumb">
            <span className="text-secondary">{currentOrg.name}</span>
            <span className="text-tertiary mx-2">/</span>
            <span className="text-primary font-medium">Dashboard</span>
          </div>
          <div className="flex items-center">
            <NotificationBell />
          </div>
        </header>
        <main className="app-content">
          <Outlet context={{ currentOrg }} />
        </main>
      </div>
      
      <CommandPalette />
    </div>
  );
}
