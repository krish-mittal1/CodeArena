/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Matchmaking Store — queue state
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import { create } from 'zustand';
import { matchmakingApi } from '../api/auth';

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

    onMatchFound: (data) => set({
        status: 'found',
        matchData: data,
    }),

    tickWait: () => set((s) => ({ waitSeconds: s.waitSeconds + 1 })),

    reset: () => set({
        status: 'idle',
        waitSeconds: 0,
        matchData: null,
        error: null,
    }),
}));
