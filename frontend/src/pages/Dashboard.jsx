import { useEffect, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useBattleStore } from '../stores/battleStore';
import { useMatchmakingStore } from '../stores/matchmakingStore';
import QueueOverlay from '../components/matchmaking/QueueOverlay';
import { formatWinRate, formatElo } from '../utils/formatters';
import styles from '../styles/dashboard.module.css';

export default function Dashboard() {
    // Use selectors for proper reactivity (Zustand best practice)
    const user = useAuthStore((s) => s.user);
    const queueStatus = useMatchmakingStore((s) => s.status);
    const joinQueue = useMatchmakingStore((s) => s.joinQueue);
    const leaveQueue = useMatchmakingStore((s) => s.leaveQueue);
    const resetQueue = useMatchmakingStore((s) => s.reset);
    const matchId = useBattleStore((s) => s.matchId);
    const hasInitializedRef = useRef(false);

    // Deterministic behavior:
    // - Landing on /dashboard should never show QueueOverlay or "searching" unless user explicitly clicked Find Match.
    // - If stale client state exists (e.g., refresh during queue, dev fast-refresh), cancel queue idempotently.
    useEffect(() => {
        if (hasInitializedRef.current) return;
        hasInitializedRef.current = true;

        if (matchId) return; // active battle route guard will handle, don't interfere

        // One-time cleanup: if we land on /dashboard with stale non-idle state (e.g., after hard refresh),
        // cancel queue idempotently and reset the store. Subsequent user-initiated joins are untouched.
        if (queueStatus !== 'idle') {
            (async () => {
                await leaveQueue(); // idempotent on backend
                resetQueue();
            })();
        }
    }, []);

    if (!user) return null;

    const winRate = formatWinRate(user.matches_won, user.matches_played);
    const isSearching = queueStatus !== 'idle';

    return (
        <div className={styles.dashboard}>
            <h1 className={styles.greeting}>
                Welcome, <span className={styles.accent}>{user.username}</span>
            </h1>
            <p className={styles.subtitle}>Ready to compete?</p>

            {/* ── Stats Grid ──────────────────────────────── */}
            <div className={styles.statsGrid}>
                <div className={styles.statCard}>
                    <div className={`${styles.statValue} ${styles.elo}`}>
                        {formatElo(user.elo)}
                    </div>
                    <div className={styles.statLabel}>ELO Rating</div>
                </div>
                <div className={styles.statCard}>
                    <div className={styles.statValue}>{user.matches_played}</div>
                    <div className={styles.statLabel}>Matches</div>
                </div>
                <div className={styles.statCard}>
                    <div className={styles.statValue}>{user.matches_won}</div>
                    <div className={styles.statLabel}>Wins</div>
                </div>
                <div className={styles.statCard}>
                    <div className={styles.statValue}>{winRate}</div>
                    <div className={styles.statLabel}>Win Rate</div>
                </div>
            </div>

            {/* ── Find Match ─────────────────────────────── */}
            <div className={styles.matchSection}>
                <h2 className={styles.matchTitle}>Ready for Battle?</h2>
                <p className={styles.matchDescription}>
                    Queue up and get matched with an opponent near your skill level
                </p>
                <button
                    className={styles.findMatchBtn}
                    onClick={joinQueue}
                    disabled={isSearching}
                >
                    {isSearching ? '⏳ Searching...' : '⚔ Find Match'}
                </button>
            </div>

            {/* ── Queue Overlay (fullscreen when searching/found) ── */}
            <QueueOverlay />
        </div>
    );
}
