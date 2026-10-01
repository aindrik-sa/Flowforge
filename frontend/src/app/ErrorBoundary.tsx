import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-screen bg-bg-1 text-primary">
          <div className="glass p-8 rounded-xl max-w-md w-full text-center">
            <AlertTriangle className="text-red-500 mx-auto mb-4" size={48} />
            <h1 className="text-xl font-bold mb-2">Something went wrong</h1>
            <p className="text-secondary text-sm mb-6">
              An unexpected error occurred. We've been notified and are looking into it.
            </p>
            <div className="bg-black/50 text-red-400 p-4 rounded text-left text-xs font-mono overflow-auto max-h-32 mb-6">
              {this.state.error?.message}
            </div>
            <button 
              className="btn btn-primary w-full"
              onClick={() => window.location.reload()}
            >
              Refresh the page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
