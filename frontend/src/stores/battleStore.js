/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Battle Store — match state during an active battle
   
   Populated by WS events: match_found, room_joined,
   submission_result, opponent_submitted, match_ended.
   Multi-problem battles: first to ACCEPTED on all problems wins.
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import { create } from 'zustand';
import { CODE_TEMPLATES, generateBoilerplate } from '../utils/constants';

function normalizeProblems(data) {
    if (Array.isArray(data.problems) && data.problems.length > 0) {
        return data.problems.map((p, i) => ({
            id: String(p.id),
            title: p.title || `Problem ${i + 1}`,
            difficulty: p.difficulty || null,
            order_index: p.order_index ?? i,
        }));
    }
    const id = data.problem_id || data.problem?.id;
    if (!id) return [];
    return [{
        id: String(id),
        title: data.problem_title || data.problem?.title || 'Problem',
        difficulty: data.problem?.difficulty || null,
        order_index: 0,
    }];
}

export const useBattleStore = create((set, get) => ({
    // ── Match metadata ─────────────────────────────
    matchId: null,
    problemId: null,
    problem: null,
    problems: [],
    problemDetails: {},
    solvedProblemIds: [],
    codesByProblem: {},
    opponent: null,
    duration: 1800,

    // ── Timer ──────────────────────────────────────
    remainingSeconds: 0,
    timerRunning: false,

    // ── Editor ─────────────────────────────────────
    language: 'cpp',
    code: CODE_TEMPLATES.cpp,

    // ── Submissions ────────────────────────────────
    submissionStatus: 'idle',    // idle | submitting | running | judged
    lastVerdict: null,
    submissionHistory: [],
    // Sample-only run (never hidden tests)
    runStatus: 'idle',           // idle | running | done | error
    runResult: null,

    // ── Opponent ───────────────────────────────────
    opponentActivity: null,
    opponentDisconnected: false,

    // ── Match result ───────────────────────────────
    matchResult: null,

    // ━━ Actions ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    setMatch: (data) => {
        const problems = normalizeProblems(data);
        const firstId = problems[0]?.id || null;
        const lang = get().language;
        const initialCode = data.problem
            ? (generateBoilerplate(lang, data.problem) || CODE_TEMPLATES[lang] || '')
            : (CODE_TEMPLATES[lang] || '');
        const solved = Array.isArray(data.solved_problem_ids)
            ? data.solved_problem_ids.map(String)
            : [];

        set({
            matchId: data.match_id,
            problemId: firstId,
            problem: data.problem || null,
            problems,
            problemDetails: data.problem?.id
                ? { [String(data.problem.id)]: data.problem }
                : {},
            solvedProblemIds: solved,
            codesByProblem: firstId ? { [firstId]: initialCode } : {},
            opponent: data.opponent || null,
            duration: data.duration_seconds || 1800,
            remainingSeconds: data.remaining_seconds ?? data.duration_seconds ?? 1800,
            timerRunning: true,
            submissionStatus: 'idle',
            lastVerdict: null,
            submissionHistory: [],
            runStatus: 'idle',
            runResult: null,
            opponentActivity: null,
            opponentDisconnected: false,
            matchResult: null,
            code: initialCode,
        });
    },

    onRoomJoined: (data) => set({
        remainingSeconds: data.remaining_seconds ?? get().remainingSeconds,
        timerRunning: true,
    }),

    setActiveProblem: (problemId) => {
        const state = get();
        const nextId = String(problemId);
        if (!nextId || nextId === state.problemId) return;

        const codesByProblem = {
            ...state.codesByProblem,
            [state.problemId]: state.code,
        };
        const details = state.problemDetails[nextId] || null;
        const nextCode = codesByProblem[nextId]
            ?? (details
                ? (generateBoilerplate(state.language, details) || CODE_TEMPLATES[state.language] || '')
                : (CODE_TEMPLATES[state.language] || ''));

        set({
            problemId: nextId,
            problem: details,
            code: nextCode,
            codesByProblem,
            submissionStatus: 'idle',
            lastVerdict: null,
            runStatus: 'idle',
            runResult: null,
        });
    },

    setLanguage: (language) => {
        const currentCode = get().code;
        const currentLang = get().language;
        const problem = get().problem;
        const isDefault = currentCode === (generateBoilerplate(currentLang, problem) || CODE_TEMPLATES[currentLang] || '') || currentCode === CODE_TEMPLATES[currentLang];

        set({
            language,
            code: isDefault
                ? (generateBoilerplate(language, problem) || CODE_TEMPLATES[language] || '')
                : currentCode,
        });
    },

    setCode: (code) => set((state) => ({
        code,
        codesByProblem: state.problemId
            ? { ...state.codesByProblem, [state.problemId]: code }
            : state.codesByProblem,
    })),

    setSubmissionStatus: (status) => set({ submissionStatus: status }),

    setRunResult: (data) => set({
        runStatus: data?.status === 'error' ? 'error' : 'done',
        runResult: data,
    }),

    setRunStatus: (status) => set({ runStatus: status }),

    clearRunResult: () => set({ runStatus: 'idle', runResult: null }),

    setVerdict: (data) => set((state) => {
        const problemId = data.problem_id ? String(data.problem_id) : state.problemId;
        const isAccepted = data.verdict === 'accepted';
        let solvedProblemIds = state.solvedProblemIds;
        if (isAccepted && problemId && !solvedProblemIds.includes(problemId)) {
            solvedProblemIds = [...solvedProblemIds, problemId];
        }
        return {
            submissionStatus: 'judged',
            lastVerdict: data,
            submissionHistory: [...state.submissionHistory, data],
            solvedProblemIds,
        };
    }),

    setOpponentActivity: (data) => set({ opponentActivity: data }),

    setOpponentDisconnected: (data) => set({ opponentDisconnected: !(data?.reconnected) }),

    setMatchResult: (data) => set({
        matchResult: data,
        timerRunning: false,
        submissionStatus: 'idle',
    }),

    syncTimer: (serverSeconds) => {
        const current = get().remainingSeconds;
        const drift = Math.abs(current - serverSeconds);
        // Snap if drift > 1s to keep client and server closely aligned
        if (drift > 1) {
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
        problems: [],
        problemDetails: {},
        solvedProblemIds: [],
        codesByProblem: {},
        opponent: null,
        duration: 1800,
        remainingSeconds: 0,
        timerRunning: false,
        language: 'cpp',
        code: CODE_TEMPLATES.cpp,
        submissionStatus: 'idle',
        lastVerdict: null,
        submissionHistory: [],
        runStatus: 'idle',
        runResult: null,
        opponentActivity: null,
        opponentDisconnected: false,
        matchResult: null,
    }),

    setProblem: (problem) => set((state) => {
        if (!problem?.id) return state;
        const pid = String(problem.id);
        const currentLang = state.language;
        const currentCode = state.code || '';
        const genericDefault = CODE_TEMPLATES[currentLang] || '';
        const previousGenerated = generateBoilerplate(currentLang, state.problem) || genericDefault;
        const nextGenerated = generateBoilerplate(currentLang, problem) || genericDefault;

        const isActive = !state.problemId || state.problemId === pid;
        const savedCode = state.codesByProblem[pid];
        const shouldReplaceCode = isActive && (
            !currentCode ||
            currentCode === genericDefault ||
            currentCode === previousGenerated
        );

        const nextCode = isActive
            ? (shouldReplaceCode ? (savedCode || nextGenerated) : currentCode)
            : state.code;

        return {
            problem: isActive ? problem : state.problem,
            problemId: state.problemId || pid,
            problemDetails: { ...state.problemDetails, [pid]: problem },
            codesByProblem: {
                ...state.codesByProblem,
                [pid]: savedCode || (isActive && shouldReplaceCode ? nextGenerated : (savedCode || nextGenerated)),
            },
            code: nextCode,
        };
    }),
}));
