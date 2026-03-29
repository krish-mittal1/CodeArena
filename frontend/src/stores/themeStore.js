import { create } from 'zustand';

const THEME_STORAGE_KEY = 'codearena_theme';
const ALLOWED_THEMES = ['default', 'dark', 'light'];

function normalizeTheme(theme) {
    return ALLOWED_THEMES.includes(theme) ? theme : 'default';
}

function applyThemeToDocument(theme) {
    if (typeof document === 'undefined') return;
    document.documentElement.setAttribute('data-theme', theme);
}

function getStoredTheme() {
    if (typeof window === 'undefined') return 'default';
    return normalizeTheme(window.localStorage.getItem(THEME_STORAGE_KEY));
}

export const useThemeStore = create((set) => ({
    theme: 'default',

    initTheme: () => {
        const savedTheme = getStoredTheme();
        applyThemeToDocument(savedTheme);
        set({ theme: savedTheme });
    },

    setTheme: (theme) => {
        const nextTheme = normalizeTheme(theme);
        applyThemeToDocument(nextTheme);
        if (typeof window !== 'undefined') {
            window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
        }
        set({ theme: nextTheme });
    },
}));
