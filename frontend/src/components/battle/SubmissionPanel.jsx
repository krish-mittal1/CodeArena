import { useBattleStore } from '../../stores/battleStore';
import { VERDICTS } from '../../utils/constants';
import styles from './SubmissionPanel.module.css';

export default function SubmissionPanel() {
    const submissionHistory = useBattleStore((s) => s.submissionHistory);
    const submissionStatus = useBattleStore((s) => s.submissionStatus);
    const opponentActivity = useBattleStore((s) => s.opponentActivity);

    return (
        <div className={styles.panel}>
            {/* Header */}
            <div className={styles.header}>
                <span className={styles.title}>
                    {submissionStatus === 'running' ? '⏳ Running...' : '📊 Submissions'}
                </span>
                <span className={styles.count}>{submissionHistory.length} attempts</span>
            </div>

            {/* Submission list */}
            <div className={styles.list}>
                {submissionHistory.length === 0 ? (
                    <div className={styles.empty}>No submissions yet</div>
                ) : (
                    [...submissionHistory].reverse().map((sub, i) => {
                        const verdict = VERDICTS[sub.verdict] || VERDICTS.queued;
                        return (
                            <div key={i} className={styles.entry}>
                                <div className={styles.entryLeft}>
                                    <span className={styles.verdictIcon}>{verdict.icon}</span>
                                    <span
                                        className={styles.verdictLabel}
                                        style={{ color: verdict.color }}
                                    >
                                        {verdict.label}
                                    </span>
                                </div>
                                <div className={styles.entryMeta}>
                                    {sub.time_ms != null && <span>{sub.time_ms}ms</span>}
                                    {sub.memory_mb != null && <span>{sub.memory_mb}MB</span>}
                                    {sub.passed_count != null && sub.total_count != null && (
                                        <span>
                                            {sub.passed_count}/{sub.total_count}
                                        </span>
                                    )}
                                </div>
                            </div>
                        );
                    })
                )}
            </div>

            {/* Opponent activity */}
            {opponentActivity && (
                <div className={styles.opponentSection}>
                    <span>👤 Opponent:</span>
                    <span className={styles.opponentActivity}>
                        {opponentActivity.verdict
                            ? `Submitted — ${VERDICTS[opponentActivity.verdict]?.label || opponentActivity.verdict}`
                            : 'Submitted a solution'}
                    </span>
                </div>
            )}
        </div>
    );
}
