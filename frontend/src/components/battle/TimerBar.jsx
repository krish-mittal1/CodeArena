import { useState } from 'react';
import { useBattleStore } from '../../stores/battleStore';
import { useAuthStore } from '../../stores/authStore';
import { useTimer } from '../../hooks/useTimer';
import { formatTime } from '../../utils/formatters';
import { matchApi } from '../../api/auth';
import styles from './TimerBar.module.css';

export default function TimerBar() {
    const { remainingSeconds } = useTimer();
    const duration = useBattleStore((s) => s.duration);
    const matchId = useBattleStore((s) => s.matchId);
    const opponent = useBattleStore((s) => s.opponent);
    const opponentDisconnected = useBattleStore((s) => s.opponentDisconnected);
    const matchResult = useBattleStore((s) => s.matchResult);
    const user = useAuthStore((s) => s.user);
    const [forfeiting, setForfeiting] = useState(false);

    const pct = duration > 0 ? (remainingSeconds / duration) * 100 : 0;
    const isWarning = remainingSeconds <= 120 && remainingSeconds > 30;
    const isCritical = remainingSeconds <= 30;

    const timerClass = [
        styles.timerDisplay,
        isWarning && styles.warning,
        isCritical && styles.critical,
    ].filter(Boolean).join(' ');

    const fillClass = [
        styles.progressFill,
        isWarning && styles.warning,
        isCritical && styles.critical,
    ].filter(Boolean).join(' ');

    const handleForfeit = async () => {
        if (!matchId || matchResult || forfeiting) return;

        const confirmed = window.confirm(
            'Are you sure you want to leave? This counts as a loss and will affect your ELO.'
        );
        if (!confirmed) return;

        setForfeiting(true);
        try {
            await matchApi.forfeit(matchId);
            // MATCH_ENDED WS event will drive UI updates
        } catch (err) {
            console.error('Failed to forfeit match:', err);
            setForfeiting(false);
        }
    };

    return (
        <div className={styles.timerBar}>
            <div className={styles.left}>
                <span className={styles.matchLabel}>⚔ Battle</span>
                <div className={timerClass}>
                    <span className={styles.timerIcon}>⏱</span>
                    {formatTime(remainingSeconds)}
                </div>
            </div>

            <div className={styles.progressTrack}>
                <div className={fillClass} style={{ width: `${pct}%` }} />
            </div>

            <div className={styles.right}>
                <div className={styles.playerInfo}>
                    {user && (
                        <div className={styles.selfTag}>
                            <span className={styles.selfLabel}>You</span>
                            <span className={styles.selfName}>{user.username}</span>
                            {user.elo != null && (
                                <span className={styles.selfElo}>{user.elo}</span>
                            )}
                        </div>
                    )}
                    {opponent && (
                        <div className={styles.opponentTag}>
                            <span className={styles.vsLabel}>vs</span>
                            <span className={styles.opponentName}>{opponent.username}</span>
                            {opponent.elo != null && (
                                <span className={styles.opponentElo}>{opponent.elo}</span>
                            )}
                            {opponentDisconnected && (
                                <span className={styles.disconnectedBadge}>Disconnected</span>
                            )}
                        </div>
                    )}
                </div>

                <button
                    type="button"
                    className={styles.forfeitBtn}
                    onClick={handleForfeit}
                    disabled={!!matchResult || forfeiting}
                >
                    {forfeiting ? '⏳ Leaving...' : 'Leave Match'}
                </button>
            </div>
        </div>
    );
}
