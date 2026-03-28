/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Auth hooks — React Query mutations + Zustand store
   
   Combines React Query (for mutation lifecycle) with
   Zustand (for persistent client state).
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { userApi } from '../api/auth';

/**
 * Login mutation — calls auth store, navigates on success.
 */
export function useLogin() {
    const login = useAuthStore((s) => s.login);
    const navigate = useNavigate();
    const location = useLocation();
    const from = location.state?.from?.pathname || '/dashboard';

    return useMutation({
        mutationFn: ({ username, password }) => login(username, password),
        onSuccess: () => navigate(from, { replace: true }),
    });
}

/**
 * Register mutation — calls auth store, navigates on success.
 */
export function useRegister() {
    const register = useAuthStore((s) => s.register);
    const navigate = useNavigate();

    return useMutation({
        mutationFn: ({ username, email, password }) =>
            register(username, email, password),
        onSuccess: () => navigate('/dashboard'),
    });
}

/**
 * Logout — clears state + cache, navigates to login.
 */
export function useLogout() {
    const logout = useAuthStore((s) => s.logout);
    const queryClient = useQueryClient();
    const navigate = useNavigate();

    return () => {
        logout();
        queryClient.clear();
        navigate('/login');
    };
}

/**
 * User profile query — fetches from /users/me.
 * Only enabled when authenticated.
 */
export function useProfile() {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

    return useQuery({
        queryKey: ['user', 'profile'],
        queryFn: userApi.getProfile,
        enabled: isAuthenticated,
        staleTime: 60_000,
    });
}

/**
 * User stats query — fetches from /users/me/stats.
 */
export function useStats() {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

    return useQuery({
        queryKey: ['user', 'stats'],
        queryFn: userApi.getStats,
        enabled: isAuthenticated,
        staleTime: 30_000,
    });
}
