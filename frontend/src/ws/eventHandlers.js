/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   WS Event Handlers — routes server events to Zustand stores
   
   This module is the glue between the raw WebSocket and
   the application state. Each handler is a pure function
   that receives event data and updates the relevant store.
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import { WS_EVENTS } from '../utils/constants';
import wsManager from './WebSocketManager';
import { useBattleStore } from '../stores/battleStore';
import { useMatchmakingStore } from '../stores/matchmakingStore';
import { useAuthStore } from '../stores/authStore';

/**
 * Safe handler wrapper that catches errors and logs them without crashing.
 */
function safeHandler(handlerName, handler) {
    return (data) => {
        try {
            handler(data);
        } catch (error) {
            console.error(`[WS] Error in ${handlerName} handler:`, error);
            // Log error details in development
            if (process.env.NODE_ENV !== 'production') {
                console.error('Event data:', data);
                console.error('Error stack:', error.stack);
            }
        }
    };
}

/**
 * Register all event handlers.
 * Returns a cleanup function that removes all listeners.
 */
export function registerEventHandlers() {
    const unsubscribers = [];

    // ── Connected acknowledgment ────────────────────────
    unsubscribers.push(
        wsManager.on(WS_EVENTS.CONNECTED, safeHandler('CONNECTED', (data) => {
            console.log('[WS] Server acknowledged connection', data);
            // Only reset matchmaking if user is NOT actively searching
            // AND not currently in a battle (matchId set in battleStore).
            // A blind reset on reconnect would kill an in-progress queue session
            // or desync battle state.
            const mmState = useMatchmakingStore.getState();
            const battleState = useBattleStore.getState();
            if (mmState.status !== 'searching' && !battleState.matchId) {
                try {
                    mmState.reset();
                } catch (e) {
                    console.error('[WS] Failed to reset matchmaking store on CONNECTED:', e);
                }
            }
        }))
    );

    // ── Match found — matchmaking succeeded ─────────────
    unsubscribers.push(
        wsManager.on(WS_EVENTS.MATCH_FOUND, safeHandler('MATCH_FOUND', (data) => {
            try {
                console.log('[WS] match_found received:', data);

                // Update matchmaking store (for QueueOverlay navigation)
                useMatchmakingStore.getState().onMatchFound(data);

                // Transform backend data structure to match frontend expectations
                // Backend sends: { match_id, problem_id, problem_title, problem?, duration_seconds, player1, player2 }
                // Frontend expects: { match_id, problem, opponent, duration_seconds }
                const currentUserId = String(useAuthStore.getState().user?.id ?? '');

                // Determine opponent (the player that's not the current user)
                let opponent = null;
                if (data.player1 && data.player2) {
                    const p1Id = String(data.player1.user_id ?? '');
                    const p2Id = String(data.player2.user_id ?? '');
                    if (p1Id === currentUserId) {
                        opponent = data.player2;
                    } else if (p2Id === currentUserId) {
                        opponent = data.player1;
                    } else {
                        opponent = data.player2;
                    }
                }

                // Transform data for battleStore
                const battleData = {
                    match_id: data.match_id,
                    problem_id: data.problem_id,
                    problem_title: data.problem_title,
                    problems: data.problems || [],
                    opponent: opponent,
                    duration_seconds: data.duration_seconds || 1800,
                };

                console.log('[WS] Setting battle store with:', battleData);
                const currentState = useBattleStore.getState();
                if (currentState.matchId === battleData.match_id) {
                    // Reconnecting to same match — only update metadata, preserve code/submissions
                    const problems = Array.isArray(battleData.problems) && battleData.problems.length
                        ? battleData.problems.map((p, i) => ({
                            id: String(p.id),
                            title: p.title || `Problem ${i + 1}`,
                            difficulty: p.difficulty || null,
                            order_index: p.order_index ?? i,
                        }))
                        : currentState.problems;
                    useBattleStore.setState({
                        opponent: battleData.opponent || currentState.opponent,
                        duration: battleData.duration_seconds || currentState.duration,
                        problems: problems.length ? problems : currentState.problems,
                    });
                } else {
                    currentState.setMatch(battleData);
                }
            } catch (error) {
                console.error('[WS] Error handling match_found:', error);
                // Re-throw to be caught by safeHandler wrapper
                throw error;
            }
        }))
    );

    // ── Room joined (includes reconnection) ─────────────
    unsubscribers.push(
        wsManager.on(WS_EVENTS.ROOM_JOINED, safeHandler('ROOM_JOINED', (data) => {
            useBattleStore.getState().onRoomJoined(data);
        }))
    );

    // ── Submission status updates ───────────────────────
    unsubscribers.push(
        wsManager.on(WS_EVENTS.SUBMISSION_RUNNING, safeHandler('SUBMISSION_RUNNING', (data) => {
            useBattleStore.getState().setSubmissionStatus('running');
        }))
    );

    unsubscribers.push(
        wsManager.on(WS_EVENTS.SUBMISSION_RESULT, safeHandler('SUBMISSION_RESULT', (data) => {
            console.log('[WS] submission_result received:', data);
            useBattleStore.getState().setVerdict(data);
        }))
    );

    // ── Opponent activity ───────────────────────────────
    unsubscribers.push(
        wsManager.on(WS_EVENTS.OPPONENT_SUBMITTED, safeHandler('OPPONENT_SUBMITTED', (data) => {
            useBattleStore.getState().setOpponentActivity(data);
        }))
    );

    // ── Match ended ─────────────────────────────────────
    unsubscribers.push(
        wsManager.on(WS_EVENTS.MATCH_ENDED, safeHandler('MATCH_ENDED', (data) => {
            console.log('[WS] match_ended received:', data);

            const battleState = useBattleStore.getState();
            const authState = useAuthStore.getState();
            const currentUserId = String(authState.user?.id ?? '');
            const opponent = battleState.opponent;

            // Data from server (via ConnectionManager.broadcast_match_ended):
            // { winner_id, winner_username, reason, your_elo_delta, new_elo }
            const winnerId = data.winner_id != null ? String(data.winner_id) : null;
            const isWinner = !!winnerId && winnerId === currentUserId;
            const isDraw = !winnerId;

            const result =
                isDraw ? (data.reason === 'timeout' ? 'time_up' : 'draw') :
                    isWinner ? 'win' : 'loss';

            const elo_change = data.your_elo_delta ?? 0;
            const opponent_username = opponent?.username || 'Your opponent';
            const winner_username = data.winner_username
                || (winnerId
                    ? (isWinner ? 'You' : opponent_username)
                    : null);

            // Update battle state
            battleState.setMatchResult({
                match_id: battleState.matchId,
                result,
                elo_change,
                winner_username,
                opponent_username,
                reason: data.reason,
                new_elo: data.new_elo,
            });

            // Refresh Navbar/Dashboard ELO from server payload
            if (data.new_elo != null && authState.user) {
                authState.setUser({ ...authState.user, elo: data.new_elo });
            }

            // Also reset matchmaking store so UI never thinks we're still queued/found
            try {
                useMatchmakingStore.getState().reset();
            } catch (e) {
                console.error('[WS] Failed to reset matchmaking store on MATCH_ENDED:', e);
            }
        }))
    );

    // ── Opponent disconnected ───────────────────────────
    unsubscribers.push(
        wsManager.on(WS_EVENTS.PLAYER_DISCONNECTED, safeHandler('PLAYER_DISCONNECTED', (data) => {
            useBattleStore.getState().setOpponentDisconnected(data);
        }))
    );

    // ── Timer sync ──────────────────────────────────────
    unsubscribers.push(
        wsManager.on(WS_EVENTS.MATCH_TIMER_SYNC, safeHandler('MATCH_TIMER_SYNC', (data) => {
            useBattleStore.getState().syncTimer(data.remaining_seconds);
        }))
    );

    // ── Server errors ───────────────────────────────────
    unsubscribers.push(
        wsManager.on(WS_EVENTS.ERROR, safeHandler('ERROR', (data) => {
            console.error('[WS] Server error:', data);
        }))
    );

    // ── Debug: log all events in development ────────────
    if (process.env.NODE_ENV !== 'production') {
        unsubscribers.push(
            wsManager.on('*', safeHandler('DEBUG_ALL', ({ event, data }) => {
                console.log(`[WS] ← ${event}`, data);
            }))
        );
    }

    // Return cleanup function
    return () => {
        unsubscribers.forEach((unsub) => unsub());
    };
}
