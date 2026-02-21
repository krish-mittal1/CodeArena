import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from './stores/authStore';
import { useWebSocket } from './hooks/useWebSocket';
import { useBattleStore } from './stores/battleStore';
import Navbar from './components/layout/Navbar';
import ProtectedRoute from './components/layout/ProtectedRoute';
import ErrorBoundary from './components/layout/ErrorBoundary';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';

import Dashboard from './pages/Dashboard';
import Battle from './pages/Battle';
import History from './pages/History';
import Profile from './pages/Profile';
import Settings from './pages/Settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30_000,
    },
  },
});

function AppRoutes() {
  const { isAuthenticated, isLoading, boot } = useAuthStore();
  const matchId = useBattleStore((s) => s.matchId);

  useWebSocket();

  useEffect(() => {
    boot();
  }, [boot]);

  useEffect(() => {
    if (!matchId) return;
    const handler = (event) => {
      event.preventDefault();
      event.returnValue = '';
      return '';
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [matchId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-bg-root flex items-center justify-center">
        <div className="text-center">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-accent to-accent-secondary flex items-center justify-center shadow-xl shadow-accent-glow/40 mb-4 animate-pulse">
            <span className="text-2xl">⚔</span>
          </div>
          <p className="text-text-secondary text-sm font-medium">Loading CodeArena...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Navbar />
      <main className="flex-1">
        <Routes>
          {/* Public */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />} />
          <Route path="/register" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Register />} />


          {/* Protected */}
          <Route
            path="/battle/:matchId"
            element={<ProtectedRoute><Battle /></ProtectedRoute>}
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                {matchId ? <Navigate to={`/battle/${matchId}`} replace /> : <Dashboard />}
              </ProtectedRoute>
            }
          />
          <Route
            path="/history"
            element={
              <ProtectedRoute>
                {matchId ? <Navigate to={`/battle/${matchId}`} replace /> : <History />}
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                {matchId ? <Navigate to={`/battle/${matchId}`} replace /> : <Profile />}
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                {matchId ? <Navigate to={`/battle/${matchId}`} replace /> : <Settings />}
              </ProtectedRoute>
            }
          />

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AppRoutes />
          <Toaster
            position="bottom-right"
            toastOptions={{
              style: {
                background: '#181828',
                color: '#e8e8f0',
                borderRadius: '12px',
                border: '1px solid #2a2a40',
                fontSize: '14px',
              },
              success: {
                iconTheme: { primary: '#00e676', secondary: '#181828' },
              },
              error: {
                iconTheme: { primary: '#ff5252', secondary: '#181828' },
              },
            }}
          />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
