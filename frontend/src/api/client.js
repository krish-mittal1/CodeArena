/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Axios instance with JWT refresh interceptor
   
   - Attaches access token to every request
   - On 401 → silently refreshes token → retries original request
   - Queues concurrent 401s (only one refresh fires)
   - On refresh failure → clear auth → redirect to /login
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import axios from 'axios';
import { API_BASE } from '../utils/constants';
import { storage } from '../utils/storage';

const api = axios.create({
    baseURL: `${API_BASE}/api/v1`,
    headers: { 'Content-Type': 'application/json' },
    timeout: 15000,
});

// ── Token injection ──────────────────────────────────

// FIX: Initialize from storage so the token survives a page refresh
let accessToken = storage.getAccessToken?.() || null;

export function setAccessToken(token) {
    accessToken = token;
}

export function getAccessToken() {
    return accessToken;
}

api.interceptors.request.use((config) => {
    // FIX: Pull from memory variable, but fallback to storage if memory is empty
    const token = accessToken || storage.getAccessToken?.();
    
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// ── Silent refresh on 401 ────────────────────────────

let isRefreshing = false;
let failedQueue = [];

function processQueue(error, token = null) {
    failedQueue.forEach(({ resolve, reject }) => {
        if (error) reject(error);
        else resolve(token);
    });
    failedQueue = [];
}

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Don't intercept refresh endpoint itself or retries
        if (
            error.response?.status !== 401 ||
            originalRequest._retry ||
            originalRequest.url?.includes('/auth/refresh') ||
            originalRequest.url?.includes('/auth/login')
        ) {
            return Promise.reject(error);
        }

        // Queue concurrent 401s
        if (isRefreshing) {
            return new Promise((resolve, reject) => {
                failedQueue.push({ resolve, reject });
            }).then((token) => {
                originalRequest.headers.Authorization = `Bearer ${token}`;
                return api(originalRequest);
            });
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
            const refreshToken = storage.getRefreshToken();
            if (!refreshToken) throw new Error('No refresh token');

            const { data } = await axios.post(`${API_BASE}/api/v1/auth/refresh`, {
                refresh_token: refreshToken,
            });

            const newAccessToken = data.access_token;
            const newRefreshToken = data.refresh_token;

            setAccessToken(newAccessToken);
            // Ensure storage is updated with both tokens
            storage.setAccessToken?.(newAccessToken); 
            storage.setRefreshToken(newRefreshToken);

            // Notify auth store
            const { useAuthStore } = await import('../stores/authStore');
            useAuthStore.getState()._setTokensSilent(newAccessToken, newRefreshToken);

            processQueue(null, newAccessToken);

            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return api(originalRequest);
        } catch (refreshError) {
            processQueue(refreshError, null);

            // Clear auth state and redirect
            setAccessToken(null);
            storage.clear();
            const { useAuthStore } = await import('../stores/authStore');
            useAuthStore.getState().logout();
            window.location.href = '/login';

            return Promise.reject(refreshError);
        } finally {
            isRefreshing = false;
        }
    }
);

export default api;