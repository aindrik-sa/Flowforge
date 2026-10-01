import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Input } from '@/shared/ui/Input';
import { Button } from '@/shared/ui/Button';
import { Layers } from 'lucide-react';
import './AuthLayout.css';

export function RegisterPage() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await register({ first_name: firstName, last_name: lastName, email, password });
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please check your details.');
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
          <h1>Join FlowForge</h1>
          <p className="text-secondary text-lg mt-2">
            Start managing your projects like a pro today.
          </p>
        </div>
      </div>

      {/* Right Side: Form */}
      <div className="auth-form-container">
        <div className="auth-form-wrapper glass">
          <h2 className="mb-2">Create an account</h2>
          <p className="text-secondary mb-8">Enter your details to get started</p>
          
          <form onSubmit={handleSubmit} className="auth-form">
            <div className="flex gap-4">
              <div className="form-group flex-1">
                <label htmlFor="firstName">First Name</label>
                <Input 
                  id="firstName" 
                  type="text" 
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  required
                />
              </div>
              <div className="form-group flex-1">
                <label htmlFor="lastName">Last Name</label>
                <Input 
                  id="lastName" 
                  type="text" 
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group mt-4">
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
              Create Account
            </Button>
            
            <p className="text-center text-secondary text-sm mt-6">
              Already have an account? <Link to="/login">Sign in</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
