import React, { useMemo } from 'react';
import { useOutletContext } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer,
  AreaChart, Area, XAxis, YAxis, CartesianGrid
} from 'recharts';
import { reportsApi } from '../api';
import type { Project } from '../../projects/types';
import { StatCard } from '../components/StatCard';
import './ProjectReportsPage.css';

export function ProjectReportsPage() {
  const { project } = useOutletContext<{ project: Project }>();

  const { data: stats, isLoading } = useQuery({
    queryKey: ['reports', 'dashboard', project.id],
    queryFn: () => reportsApi.getProjectDashboard(project.id),
  });

  // Data for Donut Chart
  const statusData = useMemo(() => {
    if (!stats) return [];
    return [
      { name: 'Completed', value: stats.completed_tasks, color: '#34d399' },
      { name: 'Pending', value: stats.pending_tasks, color: '#818cf8' },
    ];
  }, [stats]);

  // Mock data for Burndown (since backend doesn't provide historical timeseries yet)
  const burndownData = [
    { day: 'Mon', remaining: 40 },
    { day: 'Tue', remaining: 35 },
    { day: 'Wed', remaining: 32 },
    { day: 'Thu', remaining: 28 },
    { day: 'Fri', remaining: 20 },
    { day: 'Sat', remaining: 15 },
    { day: 'Sun', remaining: 5 },
  ];

  if (isLoading) {
    return <div className="p-8 text-secondary">Loading reports...</div>;
  }

  if (!stats) {
    return <div className="p-8 text-secondary">Could not load reports.</div>;
  }

  return (
    <div className="reports-page">
      <div className="reports-header mb-8 flex justify-between items-end">
        <div>
          <h2 className="text-xl font-bold mb-1">Project Dashboard</h2>
          <p className="text-secondary text-sm">Key metrics and overall progress.</p>
        </div>
        <div className="flex gap-2">
          <select className="glass px-3 py-1.5 rounded text-sm text-primary outline-none cursor-pointer">
            <option>Last 30 Days</option>
            <option>Last 7 Days</option>
            <option>All Time</option>
          </select>
          <button className="glass px-3 py-1.5 rounded text-sm text-secondary hover:text-primary">
            Export CSV
          </button>
        </div>
      </div>

      <div className="bento-grid">
        {/* Stat Cards */}
        <div className="bento-item stat-row">
          <StatCard title="Total Tasks" value={stats.total_tasks} trend={8} />
          <StatCard title="Completed" value={stats.completed_tasks} trend={12} />
          <StatCard title="Pending" value={stats.pending_tasks} trend={-3} />
          <StatCard title="Completion" value={stats.completion_percentage} suffix="%" trend={5} />
        </div>

        {/* Charts Row */}
        <div className="bento-item chart-card span-2 glass">
          <h3 className="chart-title mb-4">Sprint Burndown (Mock)</h3>
          <div className="chart-container" style={{ height: '240px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={burndownData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRemaining" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#818cf8" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#818cf8" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#9ca3af' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#9ca3af' }} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: 'rgba(30,30,36,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Area type="monotone" dataKey="remaining" stroke="#818cf8" strokeWidth={2} fillOpacity={1} fill="url(#colorRemaining)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bento-item chart-card glass">
          <h3 className="chart-title mb-4">Task Status</h3>
          <div className="chart-container flex items-center justify-center" style={{ height: '240px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  animationDuration={1500}
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: 'rgba(30,30,36,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-4 mt-2">
            {statusData.map(d => (
              <div key={d.name} className="flex items-center gap-2 text-xs text-secondary">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: d.color }}></div>
                {d.name} ({d.value})
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
