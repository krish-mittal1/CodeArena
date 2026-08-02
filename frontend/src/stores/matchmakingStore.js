/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Matchmaking Store — queue state
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import { create } from 'zustand';
import { matchmakingApi } from '../api/auth';
import { useAuthStore } from './authStore';

function resolveOpponent(data) {
    if (data?.opponent) return data.opponent;
    if (!data?.player1 || !data?.player2) return null;
    const currentUserId = String(useAuthStore.getState().user?.id ?? '');
    const p1Id = String(data.player1.user_id ?? '');
    const p2Id = String(data.player2.user_id ?? '');
    if (currentUserId && p1Id === currentUserId) return data.player2;
    if (currentUserId && p2Id === currentUserId) return data.player1;
    return data.player2;
}

export const useMatchmakingStore = create((set) => ({
    status: 'idle',           // idle | searching | found
    waitSeconds: 0,
    matchData: null,
    error: null,

    joinQueue: async () => {
        try {
            set({ status: 'searching', waitSeconds: 0, error: null });
            await matchmakingApi.join();
        } catch (err) {
            const msg = err.response?.data?.detail || 'Failed to join queue';
            set({ status: 'idle', error: msg });
        }
    },

    leaveQueue: async () => {
        try {
            await matchmakingApi.leave();
        } catch {
            // Ignore — might already be removed
        }
        set({ status: 'idle', waitSeconds: 0 });
    },

    onMatchFound: (data) => {
        const opponent = resolveOpponent(data);
        set({
            status: 'found',
            matchData: { ...data, opponent },
        });
    },

    tickWait: () => set((s) => ({ waitSeconds: s.waitSeconds + 1 })),

    reset: () => set({
        status: 'idle',
        waitSeconds: 0,
        matchData: null,
        error: null,
    }),
}));
