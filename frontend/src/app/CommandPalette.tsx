import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Folder, CheckSquare, Settings, User } from 'lucide-react';
import { useCurrentOrg } from '../features/organizations/hooks/useCurrentOrg';
import './CommandPalette.css';

interface Action {
  id: string;
  title: string;
  icon: React.ReactNode;
  perform: () => void;
}

export function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const { currentOrg } = useCurrentOrg();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd+K or Ctrl+K to toggle
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
        setQuery('');
        setSelectedIndex(0);
      }
      
      // Global shortcut C to create task (only if not focused in an input)
      if (e.key === 'c' && !e.metaKey && !e.ctrlKey) {
        if (document.activeElement?.tagName === 'INPUT' || document.activeElement?.tagName === 'TEXTAREA') return;
        e.preventDefault();
        // Here we could open a Create Task modal. For now, open command palette with "Create task" preset
        setIsOpen(true);
        setQuery('Create task');
      }

      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  const actions: Action[] = [
    {
      id: 'go-projects',
      title: 'Go to Projects',
      icon: <Folder size={16} />,
      perform: () => navigate(`/${currentOrg?.id}/projects`),
    },
    {
      id: 'create-project',
      title: 'Create new project...',
      icon: <Folder size={16} />,
      perform: () => navigate(`/${currentOrg?.id}/projects`), // Could open modal
    },
    {
      id: 'create-task',
      title: 'Create task...',
      icon: <CheckSquare size={16} />,
      perform: () => navigate(`/${currentOrg?.id}/projects`),
    },
    {
      id: 'go-settings',
      title: 'Settings',
      icon: <Settings size={16} />,
      perform: () => navigate(`/${currentOrg?.id}/settings`),
    },
    {
      id: 'go-profile',
      title: 'My Profile',
      icon: <User size={16} />,
      perform: () => navigate(`/${currentOrg?.id}/settings`),
    }
  ];

  const filteredActions = actions.filter(a => 
    a.title.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % filteredActions.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + filteredActions.length) % filteredActions.length);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const action = filteredActions[selectedIndex];
      if (action) {
        action.perform();
        setIsOpen(false);
      }
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="cmd-backdrop" onClick={() => setIsOpen(false)} />
      <div className="cmd-dialog">
        <div className="cmd-header">
          <Search className="cmd-search-icon" size={20} />
          <input
            ref={inputRef}
            className="cmd-input"
            placeholder="Type a command or search..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
          />
        </div>
        <div className="cmd-body">
          {filteredActions.length === 0 ? (
            <div className="cmd-empty">No results found.</div>
          ) : (
            <div className="cmd-list">
              {filteredActions.map((action, index) => (
                <div 
                  key={action.id} 
                  className={`cmd-item ${index === selectedIndex ? 'selected' : ''}`}
                  onClick={() => {
                    action.perform();
                    setIsOpen(false);
                  }}
                  onMouseEnter={() => setSelectedIndex(index)}
                >
                  <div className="cmd-item-icon">{action.icon}</div>
                  <div className="cmd-item-title">{action.title}</div>
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="cmd-footer">
          <span className="cmd-hint"><kbd>↑</kbd> <kbd>↓</kbd> to navigate</span>
          <span className="cmd-hint"><kbd>↵</kbd> to select</span>
          <span className="cmd-hint"><kbd>esc</kbd> to close</span>
        </div>
      </div>
    </>
  );
}
