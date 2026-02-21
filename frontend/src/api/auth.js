/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Auth API — register, login, refresh
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import api from './client';

export const authApi = {
    register: (data) => api.post('/auth/register', data).then((r) => r.data),
    login: (data) => api.post('/auth/login', data).then((r) => r.data),
    refresh: (refreshToken) =>
        api.post('/auth/refresh', { refresh_token: refreshToken }).then((r) => r.data),
};

export const userApi = {
    getProfile: () => api.get('/users/me').then((r) => r.data),
    getStats: () => api.get('/users/me/stats').then((r) => r.data),
};

export const matchmakingApi = {
    join: () => api.post('/matchmaking/join').then((r) => r.data),
    leave: () => api.delete('/matchmaking/leave').then((r) => r.data),
    status: () => api.get('/matchmaking/status').then((r) => r.data),
};

export const matchApi = {
    getMatch: (id) => api.get(`/matches/${id}`).then((r) => r.data),
    getHistory: () => api.get('/matches/history/me').then((r) => r.data),
    forfeit: (id) => api.post(`/matches/${id}/forfeit`).then((r) => r.data),
};

export const submissionApi = {
    submit: (data) => api.post('/submissions/', data).then((r) => r.data),
};

export const problemApi = {
    getAll: () => api.get('/problems/').then((r) => r.data),
    getById: (id) => api.get(`/problems/${id}`).then((r) => r.data),
};
