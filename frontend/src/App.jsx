import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './stores/authStore';
import { useWebSocket } from './hooks/useWebSocket';
import { useBattleStore } from './stores/battleStore';
import Navbar from './components/layout/Navbar';
import ProtectedRoute from './components/layout/ProtectedRoute';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Battle from './pages/Battle';

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

  // Connect/disconnect WebSocket based on auth state
  useWebSocket();

  useEffect(() => {
    boot();
  }, [boot]);

  // Warn before closing tab / refreshing while in an active match
  useEffect(() => {
    if (!matchId) return;
    const handler = (event) => {
      event.preventDefault();
      event.returnValue = '';
      return '';
    };
    window.addEventListener('beforeunload', handler);
    return () => {
      window.removeEventListener('beforeunload', handler);
    };
  }, [matchId]);

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        background: 'var(--bg-root)',
        color: 'var(--text-secondary)',
        fontSize: 'var(--font-size-lg)',
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '2rem', marginBottom: '12px' }}>⚔</div>
          Loading CodeArena...
        </div>
      </div>
    );
  }

  return (
    <>
      <Navbar />
      <main style={{ flex: 1 }}>
        <Routes>
          {/* Public */}
          <Route path="/" element={<Landing />} />
          <Route
            path="/login"
            element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />}
          />
          <Route
            path="/register"
            element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Register />}
          />

          {/* Protected */}
          <Route
            path="/battle/:matchId"
            element={
              <ProtectedRoute>
                <Battle />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                {matchId ? <Navigate to={`/battle/${matchId}`} replace /> : <Dashboard />}
              </ProtectedRoute>
            }
          />

          {/* History route reserved for future, but guard it for active matches */}
          <Route
            path="/history"
            element={
              <ProtectedRoute>
                {matchId ? <Navigate to={`/battle/${matchId}`} replace /> : <Dashboard />}
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
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
