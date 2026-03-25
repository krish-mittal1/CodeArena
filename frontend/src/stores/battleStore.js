/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Battle Store — match state during an active battle
   
   Populated by WS events: match_found, room_joined,
   submission_result, opponent_submitted, match_ended.
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import { create } from 'zustand';
import { CODE_TEMPLATES } from '../utils/constants';

export const useBattleStore = create((set, get) => ({
    // ── Match metadata ─────────────────────────────
    matchId: null,
    problemId: null,
    problem: null,
    opponent: null,
    duration: 1800,

    // ── Timer ──────────────────────────────────────
    remainingSeconds: 0,
    timerRunning: false,

    // ── Editor ─────────────────────────────────────
    language: 'python',
    code: CODE_TEMPLATES.python,

    // ── Submissions ────────────────────────────────
    submissionStatus: 'idle',    // idle | submitting | running | judged
    lastVerdict: null,
    submissionHistory: [],

    // ── Opponent ───────────────────────────────────
    opponentActivity: null,
    opponentDisconnected: false,

    // ── Match result ───────────────────────────────
    matchResult: null,

    // ━━ Actions ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    setMatch: (data) => set({
        matchId: data.match_id,
        problemId: data.problem_id || data.problem?.id || null,
        problem: data.problem || null,
        opponent: data.opponent || null,
        duration: data.duration_seconds || 1800,
        remainingSeconds: data.duration_seconds || 1800,
        timerRunning: false,
        submissionStatus: 'idle',
        lastVerdict: null,
        submissionHistory: [],
        opponentActivity: null,
        opponentDisconnected: false,
        matchResult: null,
    }),

    onRoomJoined: (data) => set({
        remainingSeconds: data.remaining_seconds ?? get().remainingSeconds,
        timerRunning: true,
    }),

    setLanguage: (language) => set({
        language,
        code: get().code === CODE_TEMPLATES[get().language]
            ? (CODE_TEMPLATES[language] || '')
            : get().code,
    }),

    setCode: (code) => set({ code }),

    setSubmissionStatus: (status) => set({ submissionStatus: status }),

    setVerdict: (data) => set((state) => ({
        submissionStatus: 'judged',
        lastVerdict: data,
        submissionHistory: [...state.submissionHistory, data],
    })),

    setOpponentActivity: (data) => set({ opponentActivity: data }),

    setOpponentDisconnected: () => set({ opponentDisconnected: true }),

    setMatchResult: (data) => set({
        matchResult: data,
        timerRunning: false,
        submissionStatus: 'idle',
    }),

    syncTimer: (serverSeconds) => {
        const current = get().remainingSeconds;
        const drift = Math.abs(current - serverSeconds);
        // Snap if drift > 2s, otherwise let local timer handle it
        if (drift > 2) {
            set({ remainingSeconds: serverSeconds });
        }
    },

    tickTimer: () => set((state) => ({
        remainingSeconds: Math.max(0, state.remainingSeconds - 1),
    })),

    reset: () => set({
        matchId: null,
        problemId: null,
        problem: null,
        opponent: null,
        duration: 1800,
        remainingSeconds: 0,
        timerRunning: false,
        language: 'python',
        code: CODE_TEMPLATES.python,
        submissionStatus: 'idle',
        lastVerdict: null,
        submissionHistory: [],
        opponentActivity: null,
        opponentDisconnected: false,
        matchResult: null,
    }),

    setProblem: (problem) => set({ problem }),
}));
