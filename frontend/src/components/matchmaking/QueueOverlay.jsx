/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   QueueOverlay — fullscreen matchmaking UI
   
   States:
     searching → pulsing swords + timer + cancel
     found     → success flash + redirect
     error     → error message + dismiss
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMatchmakingStore } from '../../stores/matchmakingStore';
import { formatTime } from '../../utils/formatters';
import styles from './QueueOverlay.module.css';

export default function QueueOverlay() {
    // Use selectors for proper reactivity (Zustand best practice)
    const status = useMatchmakingStore((s) => s.status);
    const waitSeconds = useMatchmakingStore((s) => s.waitSeconds);
    const matchData = useMatchmakingStore((s) => s.matchData);
    const error = useMatchmakingStore((s) => s.error);
    const leaveQueue = useMatchmakingStore((s) => s.leaveQueue);
    const tickWait = useMatchmakingStore((s) => s.tickWait);
    const reset = useMatchmakingStore((s) => s.reset);
    
    const navigate = useNavigate();
    const tickRef = useRef(null);
    const hasNavigatedRef = useRef(false); // Prevent double navigation

    // Log re-renders for debugging
    useEffect(() => {
        console.log('[QueueOverlay] Render - status:', status, 'matchData:', matchData);
    });

    // Tick the wait timer every second while searching
    useEffect(() => {
        if (status === 'searching') {
            tickRef.current = setInterval(() => tickWait(), 1000);
        }
        return () => {
            if (tickRef.current) clearInterval(tickRef.current);
        };
    }, [status, tickWait]);

    // Redirect to battle on match found (immediate navigation)
    useEffect(() => {
        if (status === 'found' && matchData?.match_id && !hasNavigatedRef.current) {
            console.log('[QueueOverlay] Match found! Status:', status, 'Match ID:', matchData.match_id);
            console.log('[QueueOverlay] Full matchData:', matchData);
            
            hasNavigatedRef.current = true;
            const matchId = matchData.match_id;
            
            console.log('[QueueOverlay] Navigating immediately to /battle/' + matchId);
            navigate(`/battle/${matchId}`, { replace: true });
            
            // Reset store after navigation
            setTimeout(() => {
                reset();
                hasNavigatedRef.current = false;
            }, 100);
        }
    }, [status, matchData, navigate, reset]);

    // Don't render if idle
    if (status === 'idle') return null;

    return (
        <div className={styles.overlay}>
            <div className={styles.card}>
                {/* ── Searching state ─────────────────── */}
                {status === 'searching' && (
                    <>
                        <div className={styles.swordsIcon}>⚔</div>
                        <h2 className={styles.title}>Finding Opponent</h2>
                        <p className={styles.subtitle}>
                            Matching you with a player near your skill level
                        </p>

                        <div className={styles.timer}>{formatTime(waitSeconds)}</div>
                        <div className={styles.timerLabel}>Time in Queue</div>

                        <div className={styles.dots}>
                            <span className={styles.dot} />
                            <span className={styles.dot} />
                            <span className={styles.dot} />
                        </div>

                        {error && <div className={styles.error}>{error}</div>}

                        <button onClick={leaveQueue} className={styles.cancelBtn}>
                            Cancel
                        </button>
                    </>
                )}

                {/* ── Match found state ───────────────── */}
                {status === 'found' && (
                    <>
                        <div className={styles.foundIcon}>🎯</div>
                        <h2 className={styles.foundTitle}>Match Found!</h2>
                        <p className={styles.foundSubtitle}>
                            Opponent: <strong>{matchData?.opponent?.username ?? 'Unknown'}</strong>
                            {matchData?.opponent?.elo && (
                                <> · ELO {matchData.opponent.elo}</>
                            )}
                        </p>
                    </>
                )}
            </div>
        </div>
    );
}
