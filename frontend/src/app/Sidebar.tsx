import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { Layers, LogOut, Briefcase, LayoutDashboard, Settings, Users } from 'lucide-react';
import { useAuth } from '../features/auth/hooks/useAuth';
import type { Organization } from '../features/organizations/types';
import { ConnectionStatus } from '../features/notifications/components/ConnectionStatus';
import './Sidebar.css';

interface SidebarProps {
  currentOrg: Organization;
}

export function Sidebar({ currentOrg }: SidebarProps) {
  const { logout, user } = useAuth();
  const orgPath = `/${currentOrg.id}`;

  return (
    <nav className="app-sidebar glass">
      <div className="sidebar-org-switcher">
        <div className="org-avatar">
          {currentOrg.name.charAt(0).toUpperCase()}
        </div>
        <div className="org-info truncate">
          <span className="org-name font-medium">{currentOrg.name}</span>
          <span className="org-plan text-xs text-secondary">Free Plan</span>
        </div>
      </div>
      
      <div className="sidebar-menu">
        <NavLink to={orgPath} end className={({ isActive }) => `sidebar-item ${isActive ? 'active' : ''}`}>
          <LayoutDashboard size={18} />
          <span>Dashboard</span>
        </NavLink>
        <NavLink to={`${orgPath}/projects`} className={({ isActive }) => `sidebar-item ${isActive ? 'active' : ''}`}>
          <Briefcase size={18} />
          <span>Projects</span>
        </NavLink>
        <NavLink to={`${orgPath}/members`} className={({ isActive }) => `sidebar-item ${isActive ? 'active' : ''}`}>
          <Users size={18} />
          <span>Members</span>
        </NavLink>
        <NavLink to={`${orgPath}/settings`} className={({ isActive }) => `sidebar-item ${isActive ? 'active' : ''}`}>
          <Settings size={18} />
          <span>Settings</span>
        </NavLink>
      </div>

      <ConnectionStatus />
      
      <div className="sidebar-footer">
        <div className="user-profile mb-4">
          <div className="user-avatar">{user?.first_name?.charAt(0) || 'U'}</div>
          <div className="truncate text-sm">
            <div>{user?.first_name} {user?.last_name}</div>
            <div className="text-secondary text-xs">{user?.email}</div>
          </div>
        </div>
        <button onClick={logout} className="sidebar-item w-full">
          <LogOut size={18} />
          <span>Log out</span>
        </button>
      </div>
    </nav>
  );
}
