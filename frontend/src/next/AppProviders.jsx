import { useEffect, useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from '../stores/authStore';
import { useWebSocket } from '../hooks/useWebSocket';
import { useBattleStore } from '../stores/battleStore';
import { useThemeStore } from '../stores/themeStore';
import Navbar from '../components/layout/Navbar';
import ErrorBoundary from '../components/layout/ErrorBoundary';

function AppBootstrap({ children }) {
    const { boot } = useAuthStore();
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

    return (
        <>
            <Navbar />
            <main className="flex-1">{children}</main>
        </>
    );
}

export default function AppProviders({ children }) {
    const [queryClient] = useState(() => new QueryClient({
        defaultOptions: {
            queries: {
                refetchOnWindowFocus: false,
                retry: 1,
                staleTime: 30_000,
            },
        },
    }));

    return (
        <ErrorBoundary>
            <QueryClientProvider client={queryClient}>
                <AppBootstrap>{children}</AppBootstrap>
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
            </QueryClientProvider>
        </ErrorBoundary>
    );
}
