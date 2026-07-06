/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Auth API — register, login, refresh
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import api from './client';

export const authApi = {
    register: (data) => api.post('/auth/register', data).then((r) => r.data),
    login: (data) => api.post('/auth/login', data).then((r) => r.data),
    refresh: (refreshToken) =>
        api.post('/auth/refresh', { refresh_token: refreshToken }).then((r) => r.data),

    // OTP
    requestOTP: (email) => api.post('/auth/request-otp', { email }).then((r) => r.data),
    verifyOTP: (email, otp) => api.post('/auth/verify-otp', { email, otp }).then((r) => r.data),
    verifyOTPOnly: (email, otp) => api.post('/auth/verify-otp-only', { email, otp }).then((r) => r.data),
};

export const userApi = {
    getProfile: () => api.get('/users/me').then((r) => r.data),
    getStats: () => api.get('/users/me/stats').then((r) => r.data),
    completeOnboarding: (data) => api.post('/users/me/onboarding', data).then((r) => r.data),
    getProgress: () => api.get('/users/me/progress').then((r) => r.data),
    getReviewQueue: () => api.get('/users/me/review-queue').then((r) => r.data),
    completeReview: (reviewId) => api.post(`/users/me/review-queue/${reviewId}/complete`).then((r) => r.data),
    getDailyProblem: () => api.get('/users/me/daily-problem').then((r) => r.data),
};

export const insightsApi = {
    list: (params) => api.get('/insights', { params }).then((r) => r.data),
    get: (id) => api.get(`/insights/${id}`).then((r) => r.data),
    getShared: (slug) => api.get(`/insights/share/${slug}`).then((r) => r.data),
};

export const mockInterviewApi = {
    start: (company) => api.post('/mock-interview/start', { company }).then((r) => r.data),
    getSession: (id) => api.get(`/mock-interview/session/${id}`).then((r) => r.data),
    recordSubmission: (sessionId, problemId, submissionId) =>
        api.post(`/mock-interview/session/${sessionId}/record`, {
            problem_id: problemId,
            submission_id: submissionId,
        }).then((r) => r.data),
    debrief: (data) => api.post('/mock-interview/debrief', data).then((r) => r.data),
};

export const statsApi = {
    getPlatform: () => api.get('/stats/platform').then((r) => r.data),
};

export const leaderboardApi = {
    get: (period = 'all_time', limit = 100) =>
        api.get('/leaderboard', { params: { period, limit } }).then((r) => r.data),
};

export const eventsApi = {
    getActive: () => api.get('/events/active').then((r) => r.data),
    getLeaderboard: (eventId, limit = 50) =>
        api.get(`/events/${eventId}/leaderboard`, { params: { limit } }).then((r) => r.data),
};

export const matchmakingApi = {
    join: () => api.post('/matchmaking/join').then((r) => r.data),
    joinTutorial: () => api.post('/matchmaking/join/tutorial').then((r) => r.data),
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
    getRecap: (id) => api.get(`/matches/recap/${id}`).then((r) => r.data),
    forfeit: (id) => api.post(`/matches/${id}/forfeit`).then((r) => r.data),
};

export const submissionApi = {
    submit: (data) => api.post('/submissions/', data).then((r) => r.data),
};

export const problemApi = {
    getAll: () => api.get('/problems/').then((r) => r.data),
    getCatalog: (params = {}) => api.get('/problems/catalog', { params }).then((r) => r.data),
    getById: (id) => api.get(`/problems/${id}`).then((r) => r.data),
};

export const practiceApi = {
    run: (data) => api.post('/practice/run', data).then((r) => r.data),
    submit: (data) => api.post('/practice/submit', data).then((r) => r.data),
    getSubmissions: (problemId) => api.get(`/practice/submissions/${problemId}`).then((r) => r.data),
    analyze: (data) => api.post('/practice/analyze', data).then((r) => r.data),
    analyzeMatch: (matchId) => api.post(`/practice/analyze/match/${matchId}`).then((r) => r.data),
    getHint: (data) => api.post('/practice/hint', data).then((r) => r.data),
    recordSolve: (problemId) => api.post('/practice/record-solve', { problem_id: problemId }).then((r) => r.data),
};

