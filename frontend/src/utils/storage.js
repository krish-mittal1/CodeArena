/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Secure token storage — only refresh token persists
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

const REFRESH_TOKEN_KEY = 'codearena_refresh_token';

export const storage = {
    getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
    setRefreshToken: (token) => localStorage.setItem(REFRESH_TOKEN_KEY, token),
    clearRefreshToken: () => localStorage.removeItem(REFRESH_TOKEN_KEY),
    clear: () => {
        localStorage.removeItem(REFRESH_TOKEN_KEY);
    },
};
