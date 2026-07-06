/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Auth Store — Zustand
   
   Access token: in-memory only (XSS-safe)
   Refresh token: localStorage (survives tab close)
   
   On app boot: tries silent refresh if refresh token exists
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import { create } from 'zustand';
import { storage } from '../utils/storage';
import { setAccessToken } from '../api/client';
import { authApi, userApi } from '../api/auth';

export const useAuthStore = create((set, get) => ({
    // ── State ───────────────────────────────────────
    user: null,
    isAuthenticated: false,
    isLoading: true,          // true until initial boot completes
    _storageListenerAttached: false,

    // ── Actions ─────────────────────────────────────

    /**
     * Register → login → fetch profile → navigate
     */
    register: async (username, email, password) => {
        const tokens = await authApi.register({ username, email, password });
        await get()._handleTokens(tokens);
    },

    /**
     * Login → load profile
     */
    login: async (username, password) => {
        const tokens = await authApi.login({ username, password });
        await get()._handleTokens(tokens);
    },

    /**
     * Logout — clear everything
     */
    logout: () => {
        setAccessToken(null);
        storage.clear();
        set({ user: null, isAuthenticated: false, isLoading: false });
    },

    setUser: (user) => set({ user }),

    /**
     * Boot — called once on app mount.
     * If refresh token exists, try silent refresh.
     * Also sets up cross-tab logout synchronization.
     */
    boot: async () => {
        // Listen for logout in other tabs (idempotent — only attach once)
        if (!get()._storageListenerAttached) {
            set({ _storageListenerAttached: true });
            window.addEventListener('storage', (event) => {
                if (event.key === null || event.key === 'refresh_token') {
                    if (!storage.getRefreshToken()) {
                        setAccessToken(null);
                        set({ user: null, isAuthenticated: false, isLoading: false });
                    }
                }
            });
        }

        const refreshToken = storage.getRefreshToken();
        if (!refreshToken) {
            set({ isLoading: false });
            return;
        }

        try {
            const tokens = await authApi.refresh(refreshToken);
            await get()._handleTokens(tokens);
        } catch {
            // Refresh token expired or invalid
            storage.clear();
            set({ isLoading: false });
        }
    },

    // ── Internal ────────────────────────────────────

    /**
     * Process token response: store tokens + fetch user profile
     */
    _handleTokens: async (tokens) => {
        setAccessToken(tokens.access_token);
        storage.setRefreshToken(tokens.refresh_token);

        try {
            const user = await userApi.getProfile();
            set({ user, isAuthenticated: true, isLoading: false });
        } catch {
            set({ isAuthenticated: true, isLoading: false });
        }
    },

    /**
     * Called by interceptor during silent refresh — no profile refetch
     */
    _setTokensSilent: (accessToken, refreshToken) => {
        setAccessToken(accessToken);
        storage.setRefreshToken(refreshToken);
    },
}));
