import { Routes, Route, Navigate } from 'react-router-dom';
import { UIGallery } from './app/UIGallery';
import { ProtectedRoute } from './features/auth/components/ProtectedRoute';
import { PublicOnlyRoute } from './features/auth/components/PublicOnlyRoute';
import { LoginPage } from './features/auth/pages/LoginPage';
import { RegisterPage } from './features/auth/pages/RegisterPage';
import { AppShell } from './app/AppShell';
import { OrgOnboarding } from './features/organizations/pages/OrgOnboarding';
import { ProjectsPage } from './features/projects/pages/ProjectsPage';
import { ProjectLayout } from './features/projects/pages/ProjectLayout';
import { ProjectSettingsPage } from './features/projects/pages/ProjectSettingsPage';
import { BoardPage } from './features/board/pages/BoardPage';
import { ProjectReportsPage } from './features/reports/pages/ProjectReportsPage';
import './App.css';

function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route element={<PublicOnlyRoute />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      {/* Development Routes */}
      <Route path="/__ui" element={<UIGallery />} />

      {/* Protected Routes */}
      <Route element={<ProtectedRoute />}>
        <Route path="/onboarding" element={<OrgOnboarding />} />
        
        {/* App Shell wrapping organization routes */}
        <Route path="/:orgId" element={<AppShell />}>
          <Route index element={<DashboardPlaceholder />} />
          
          <Route path="projects">
            <Route index element={<ProjectsPage />} />
            <Route path=":projectId" element={<ProjectLayout />}>
              <Route index element={<Navigate to="board" replace />} />
              <Route path="board" element={<BoardPage />} />
              <Route path="list" element={<div className="p-8"><h2>List View</h2></div>} />
              <Route path="reports" element={<ProjectReportsPage />} />
              <Route path="settings" element={<ProjectSettingsPage />} />
            </Route>
          </Route>
          
          <Route path="members" element={<div><h2>Members</h2></div>} />
          <Route path="settings" element={<div><h2>Settings</h2></div>} />
        </Route>

        {/* Fallback for authenticated root -> redirect to an org */}
        <Route path="/" element={<AppShell />} />
      </Route>
    </Routes>
  );
}

function DashboardPlaceholder() {
  return (
    <div className="dashboard">
      <header className="page-header" style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between' }}>
        <div>
          <h1>Welcome back</h1>
          <p className="text-secondary" style={{ marginTop: '4px' }}>Here is what's happening with your projects today.</p>
        </div>
        <button className="btn btn-primary">+ Create Task</button>
      </header>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '24px', marginBottom: '40px' }}>
        <div className="glass" style={{ padding: '24px', borderRadius: 'var(--radius-md)' }}>
          <h3 className="text-secondary font-medium text-sm">Completed Tasks</h3>
          <p style={{ fontSize: '32px', fontWeight: 700 }}>24</p>
        </div>
        <div className="glass" style={{ padding: '24px', borderRadius: 'var(--radius-md)' }}>
          <h3 className="text-secondary font-medium text-sm">Pending Review</h3>
          <p style={{ fontSize: '32px', fontWeight: 700 }}>7</p>
        </div>
      </div>
    </div>
  );
}

export default App;
