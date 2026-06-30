import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { FileText, History, Upload, LogOut, LogIn } from 'lucide-react';
import { clsx } from 'clsx';
import { getToken, logout, issueTestToken } from '@/services/api';
import { useState } from 'react';

function Navbar() {
  const navigate = useNavigate();
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const isAuthenticated = !!getToken();

  async function handleLogin() {
    setIsLoggingIn(true);
    try {
      await issueTestToken();
      navigate('/upload');
    } finally {
      setIsLoggingIn(false);
    }
  }

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto max-w-5xl flex items-center justify-between px-4 h-14">
        <NavLink to="/" className="flex items-center gap-2 font-semibold text-gray-900">
          <FileText className="h-5 w-5 text-blue-600" />
          Contract Analyzer
        </NavLink>

        {isAuthenticated && (
          <nav className="flex items-center gap-1">
            <NavLink
              to="/upload"
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100',
                )
              }
            >
              <Upload className="h-4 w-4" />
              Upload
            </NavLink>
            <NavLink
              to="/history"
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100',
                )
              }
            >
              <History className="h-4 w-4" />
              History
            </NavLink>
          </nav>
        )}

        <div>
          {isAuthenticated ? (
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm text-gray-500 hover:text-red-600 hover:bg-red-50 transition-colors"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          ) : (
            <button
              onClick={handleLogin}
              disabled={isLoggingIn}
              className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              <LogIn className="h-4 w-4" />
              {isLoggingIn ? 'Signing in...' : 'Sign In'}
            </button>
          )}
        </div>
      </div>
    </header>
  );
}

export function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main>
        <Outlet />
      </main>
    </div>
  );
}
