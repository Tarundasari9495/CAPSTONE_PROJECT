import { useNavigate } from 'react-router-dom';
import { FileText, LogIn } from 'lucide-react';
import { issueTestToken } from '@/services/api';
import { useState } from 'react';

export function LoginPage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  async function handleLogin() {
    setIsLoading(true);
    try {
      await issueTestToken();
      navigate('/upload');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-[80vh] flex-col items-center justify-center px-4">
      <div className="w-full max-w-sm rounded-2xl border border-gray-200 bg-white p-8 shadow-sm text-center">
        <div className="flex justify-center mb-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-50">
            <FileText className="h-7 w-7 text-blue-600" />
          </div>
        </div>
        <h1 className="text-xl font-bold text-gray-900">Contract Analysis Tool</h1>
        <p className="mt-1 text-sm text-gray-500">AI-Forge 2026 · Capstone Project 9</p>

        <button
          onClick={handleLogin}
          disabled={isLoading}
          className="mt-6 w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          <LogIn className="h-4 w-4" />
          {isLoading ? 'Signing in...' : 'Sign In'}
        </button>
      </div>
    </div>
  );
}
