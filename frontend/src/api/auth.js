/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Auth API — register, login, refresh
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import api from './client';

export const authApi = {
    register: (data) => api.post('/auth/register', data).then((r) => r.data),
    login: (data) => api.post('/auth/login', data).then((r) => r.data),
    refresh: (refreshToken) =>
        api.post('/auth/refresh', { refresh_token: refreshToken }).then((r) => r.data),
    verifyEmail: (token) => api.get(`/auth/verify-email?token=${token}`).then((r) => r.data),
    resendVerification: (data) => api.post('/auth/resend-verification', data).then((r) => r.data),

    // OTP
    requestOTP: (email) => api.post('/auth/request-otp', { email }).then((r) => r.data),
    verifyOTP: (email, otp) => api.post('/auth/verify-otp', { email, otp }).then((r) => r.data),
    verifyOTPOnly: (email, otp) => api.post('/auth/verify-otp-only', { email, otp }).then((r) => r.data),
};

export const userApi = {
    getProfile: () => api.get('/users/me').then((r) => r.data),
    getStats: () => api.get('/users/me/stats').then((r) => r.data),
};

export const matchmakingApi = {
    join: () => api.post('/matchmaking/join').then((r) => r.data),
    leave: () => api.delete('/matchmaking/leave').then((r) => r.data),
    status: () => api.get('/matchmaking/status').then((r) => r.data),
    
    // Private Rooms
    createPrivateRoom: () => api.post('/matchmaking/private/create').then((r) => r.data),
    joinPrivateRoom: (code) => api.post('/matchmaking/private/join', { code }).then((r) => r.data),
    getPrivateRoomStatus: (code) => api.get(`/matchmaking/private/status/${code}`).then((r) => r.data),
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

export const practiceApi = {
    submit: (data) => api.post('/practice/submit', data).then((r) => r.data),
    getSubmissions: (problemId) => api.get(`/practice/submissions/${problemId}`).then((r) => r.data),
};

