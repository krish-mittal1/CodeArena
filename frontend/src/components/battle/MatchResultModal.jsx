import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useBattleStore } from '../../stores/battleStore';
import { formatEloDelta } from '../../utils/formatters';
import styles from './MatchResultModal.module.css';

export default function MatchResultModal() {
    const matchResult = useBattleStore((s) => s.matchResult);
    const reset = useBattleStore((s) => s.reset);
    const navigate = useNavigate();

    useEffect(() => {
        if (!matchResult) return;
        const timeout = setTimeout(() => {
            reset();
            navigate('/dashboard');
        }, 5000);
        return () => clearTimeout(timeout);
    }, [matchResult, reset, navigate]);

    if (!matchResult) return null;

    const { result, elo_change, winner_username, reason } = matchResult;

    const isWin = result === 'win';
    const isLoss = result === 'loss';
    const isDraw = result === 'draw' || result === 'time_up';

    const icon = isWin ? '🏆' : isLoss ? '💀' : '🤝';
    const title = isWin ? 'Victory!' : isLoss ? 'Defeat' : (reason === 'forfeit' ? 'Forfeit' : 'Draw');
    const resultClass = isWin ? 'win' : isLoss ? 'loss' : 'draw';

    const handleDashboard = () => {
        reset();
        navigate('/dashboard');
    };

    return (
        <div className={styles.overlay}>
            <div className={`${styles.modal} ${styles[resultClass]}`}>
                <div className={styles.icon}>{icon}</div>
                <h2 className={`${styles.title} ${styles[resultClass]}`}>{title}</h2>
                <p className={styles.subtitle}>
                    {isWin && (reason === 'forfeit'
                        ? `${winner_username || 'Your opponent'} forfeited the match.`
                        : `You solved the problem before ${winner_username || 'your opponent'}!`)}
                    {isLoss && (reason === 'forfeit'
                        ? 'You forfeited the match.'
                        : `${winner_username || 'Your opponent'} solved it first.`)}
                    {isDraw && reason !== 'forfeit' && 'Neither player solved the problem in time.'}
                </p>

                <div className={styles.statsRow}>
                    {elo_change != null && (
                        <div className={styles.stat}>
                            <div
                                className={`${styles.statValue} ${elo_change >= 0 ? styles.positive : styles.negative}`}
                            >
                                {formatEloDelta(elo_change)}
                            </div>
                            <div className={styles.statLabel}>ELO</div>
                        </div>
                    )}
                </div>

                <div className={styles.actions}>
                    <button className={styles.secondaryBtn} onClick={handleDashboard}>
                        Go to Dashboard
                    </button>
                </div>
            </div>
        </div>
    );
}
