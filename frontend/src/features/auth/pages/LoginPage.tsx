import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Input } from '@/shared/ui/Input';
import { Button } from '@/shared/ui/Button';
import { Layers } from 'lucide-react';
import './AuthLayout.css';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login({ email, password });
      navigate('/');
    } catch (err: any) {
      if (err.response?.status === 401) {
        setError('Invalid email or password.');
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    }
  };

  return (
    <div className="auth-layout">
      {/* Left Side: Animated Mesh Background */}
      <div className="auth-mesh-bg">
        <div className="auth-mesh-content">
          <div className="logo-icon logo-large mb-4">
            <Layers size={32} />
          </div>
          <h1>FlowForge</h1>
          <p className="text-secondary text-lg mt-2">
            The enterprise project management tool designed for speed and clarity.
          </p>
        </div>
      </div>

      {/* Right Side: Form */}
      <div className="auth-form-container">
        <div className="auth-form-wrapper glass">
          <h2 className="mb-2">Welcome back</h2>
          <p className="text-secondary mb-8">Sign in to your account to continue</p>
          
          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <Input 
                id="email" 
                type="email" 
                placeholder="name@company.com" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            
            <div className="form-group mt-4">
              <label htmlFor="password">Password</label>
              <Input 
                id="password" 
                type="password" 
                placeholder="••••••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            {error && (
              <div className="auth-error shake">
                {error}
              </div>
            )}
            
            <Button type="submit" variant="primary" className="w-full mt-8">
              Sign In
            </Button>
            
            <p className="text-center text-secondary text-sm mt-6">
              Don't have an account? <Link to="/register">Create one</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
