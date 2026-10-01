import React, { useEffect, useState } from 'react';
import '../pages/ProjectReportsPage.css';

interface StatCardProps {
  title: string;
  value: number;
  suffix?: string;
  trend?: number; // e.g., 12 for +12%, -5 for -5%
}

export function StatCard({ title, value, suffix = '', trend }: StatCardProps) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    // Count-up animation
    let start = 0;
    const end = value;
    if (start === end) return;
    
    const duration = 1000;
    const incrementTime = Math.max(duration / end, 16);
    
    const timer = setInterval(() => {
      start += Math.ceil(end / (duration / incrementTime));
      if (start >= end) {
        setDisplayValue(end);
        clearInterval(timer);
      } else {
        setDisplayValue(start);
      }
    }, incrementTime);

    return () => clearInterval(timer);
  }, [value]);

  return (
    <div className="stat-card glass">
      <h3 className="stat-title">{title}</h3>
      <div className="stat-value-container">
        <span className="stat-value text-gradient">{displayValue}{suffix}</span>
        {trend !== undefined && (
          <span className={`stat-trend ${trend >= 0 ? 'trend-up' : 'trend-down'}`}>
            {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </span>
        )}
      </div>
      <div className="stat-sparkline">
        {/* Simple mock sparkline using SVG */}
        <svg viewBox="0 0 100 20" className="w-full h-8 opacity-50">
          <path 
            d="M0 15 L20 10 L40 18 L60 5 L80 12 L100 2" 
            fill="none" 
            stroke="var(--accent-indigo)" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
          />
        </svg>
      </div>
    </div>
  );
}
