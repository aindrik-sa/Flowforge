import React, { useState, useEffect, useRef } from 'react';
import './EditableField.css';

interface EditableFieldProps {
  value: string;
  onSave: (val: string) => void;
  type?: 'text' | 'textarea';
  className?: string;
  placeholder?: string;
}

export function EditableField({ value, onSave, type = 'text', className = '', placeholder }: EditableFieldProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [localValue, setLocalValue] = useState(value);
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isEditing]);

  const handleBlur = () => {
    setIsEditing(false);
    if (localValue !== value) {
      onSave(localValue);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && type === 'text') {
      handleBlur();
    } else if (e.key === 'Escape') {
      setLocalValue(value);
      setIsEditing(false);
    }
  };

  if (isEditing) {
    if (type === 'textarea') {
      return (
        <textarea
          ref={inputRef as any}
          className={`editable-input textarea ${className}`}
          value={localValue}
          onChange={(e) => setLocalValue(e.target.value)}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
        />
      );
    }
    return (
      <input
        ref={inputRef as any}
        type="text"
        className={`editable-input ${className}`}
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
      />
    );
  }

  return (
    <div 
      className={`editable-display ${className} ${!localValue ? 'is-empty' : ''}`}
      onClick={() => setIsEditing(true)}
    >
      {localValue || placeholder || 'Empty'}
    </div>
  );
}
