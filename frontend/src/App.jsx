import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from './stores/authStore';
import { useWebSocket } from './hooks/useWebSocket';
import { useBattleStore } from './stores/battleStore';
import { useThemeStore } from './stores/themeStore';
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
import Problems from './pages/Problems';
import Practice from './pages/Practice';
import CompanyProblems from './pages/CompanyProblems';
import DsaPracticeHub from './pages/DsaPracticeHub';
import CompetitiveProblems from './pages/CompetitiveProblems';
import Leaderboard from './pages/Leaderboard';
import Spectate from './pages/Spectate';
import MatchRecap from './pages/MatchRecap';

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
  const initTheme = useThemeStore((s) => s.initTheme);

  useWebSocket();

  useEffect(() => {
    boot();
  }, [boot]);

  useEffect(() => {
    initTheme();
  }, [initTheme]);

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
          <div className="w-14 h-14 mx-auto rounded-xl bg-accent flex items-center justify-center mb-4 animate-pulse">
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
          <Route path="/recap/:matchId" element={<MatchRecap />} />


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

          <Route
            path="/problems"
            element={
              <ProtectedRoute>
                {matchId ? <Navigate to={`/battle/${matchId}`} replace /> : <Problems />}
              </ProtectedRoute>
            }
          />
          <Route
            path="/practice/dsa"
            element={
              <ProtectedRoute>
                {matchId ? <Navigate to={`/battle/${matchId}`} replace /> : <DsaPracticeHub />}
              </ProtectedRoute>
            }
          />
          <Route
            path="/practice/competitive"
            element={
              <ProtectedRoute>
                {matchId ? <Navigate to={`/battle/${matchId}`} replace /> : <CompetitiveProblems />}
              </ProtectedRoute>
            }
          />
          <Route
            path="/practice/:problemId"
            element={
              <ProtectedRoute>
                <Practice />
              </ProtectedRoute>
            }
          />
          <Route
            path="/leaderboard"
            element={
              <ProtectedRoute>
                {matchId ? <Navigate to={`/battle/${matchId}`} replace /> : <Leaderboard />}
              </ProtectedRoute>
            }
          />
          <Route
            path="/spectate/:matchId"
            element={
              <ProtectedRoute>
                <Spectate />
              </ProtectedRoute>
            }
          />
          <Route
            path="/company/:companyId"
            element={
              <ProtectedRoute>
                {matchId ? <Navigate to={`/battle/${matchId}`} replace /> : <CompanyProblems />}
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
                background: 'var(--color-bg-primary)',
                color: 'var(--color-text-primary)',
                borderRadius: '8px',
                border: '1px solid var(--color-border)',
              },
              success: {
                iconTheme: { primary: '#22c55e', secondary: 'var(--color-bg-primary)' },
              },
              error: {
                iconTheme: { primary: '#ef4444', secondary: 'var(--color-bg-primary)' },
              },
            }}
          />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
