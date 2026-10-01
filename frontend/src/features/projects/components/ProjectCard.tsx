import React, { useRef, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MoreHorizontal } from 'lucide-react';
import type { Project } from '../types';
import './ProjectCard.css';

interface ProjectCardProps {
  project: Project;
  index: number;
}

export function ProjectCard({ project, index }: ProjectCardProps) {
  const cardRef = useRef<HTMLAnchorElement>(null);
  
  // Spotlight effect
  const handleMouseMove = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    cardRef.current.style.setProperty('--mouse-x', `${x}px`);
    cardRef.current.style.setProperty('--mouse-y', `${y}px`);
  };

  return (
    <Link 
      to={`${project.id}`} 
      ref={cardRef}
      className="project-card glass"
      onMouseMove={handleMouseMove}
      style={{ animationDelay: `${index * 50}ms` } as React.CSSProperties}
    >
      <div className="project-card-border"></div>
      <div className="project-card-content">
        <div className="flex justify-between items-start mb-4">
          <div className="project-icon-tile">
            {project.key.substring(0, 2)}
          </div>
          <button className="icon-btn text-secondary" onClick={(e) => e.preventDefault()}>
            <MoreHorizontal size={16} />
          </button>
        </div>
        
        <h3 className="project-title truncate">{project.name}</h3>
        <p className="project-key text-xs text-secondary mt-1">{project.key}</p>
        
        <div className="project-footer mt-auto pt-6 flex justify-between items-end">
          <div className="project-status">
            <span className={`status-badge status-${project.status}`}>
              {project.status.replace('_', ' ')}
            </span>
          </div>
          
          <div className="avatar-stack">
            {/* Hardcoded avatars for aesthetic demo */}
            <div className="avatar" style={{ zIndex: 3, backgroundImage: 'url(https://i.pravatar.cc/150?u=1)' }}></div>
            <div className="avatar" style={{ zIndex: 2, backgroundImage: 'url(https://i.pravatar.cc/150?u=2)' }}></div>
            <div className="avatar" style={{ zIndex: 1, backgroundImage: 'url(https://i.pravatar.cc/150?u=3)' }}></div>
          </div>
        </div>
      </div>
    </Link>
  );
}
