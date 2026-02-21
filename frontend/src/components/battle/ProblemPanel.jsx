import { useBattleStore } from '../../stores/battleStore';
import styles from './ProblemPanel.module.css';

export default function ProblemPanel() {
    const problem = useBattleStore((s) => s.problem);

    if (!problem) {
        return (
            <div className={styles.panel}>
                <div className={styles.placeholder}>Waiting for problem...</div>
            </div>
        );
    }

    const difficultyClass = {
        easy: styles.easy,
        medium: styles.medium,
        hard: styles.hard,
    }[problem.difficulty?.toLowerCase()] || '';

    return (
        <div className={styles.panel}>
            {/* Header */}
            <div className={styles.header}>
                <span className={styles.headerTitle}>📄 Problem</span>
                {problem.difficulty && (
                    <span className={`${styles.difficulty} ${difficultyClass}`}>
                        {problem.difficulty}
                    </span>
                )}
            </div>

            {/* Scrollable content */}
            <div className={styles.content}>
                <h2 className={styles.title}>{problem.title}</h2>
                <div className={styles.description}>{problem.description}</div>

                {/* Constraints */}
                {(problem.time_limit_ms || problem.memory_limit_mb) && (
                    <div className={styles.constraints}>
                        <h3 className={styles.constraintsTitle}>Constraints</h3>
                        <ul className={styles.constraintsList}>
                            {problem.time_limit_ms && (
                                <li className={styles.constraint}>
                                    ⏱ Time Limit: {problem.time_limit_ms}ms
                                </li>
                            )}
                            {problem.memory_limit_mb && (
                                <li className={styles.constraint}>
                                    💾 Memory Limit: {problem.memory_limit_mb}MB
                                </li>
                            )}
                        </ul>
                    </div>
                )}

                {/* Examples */}
                {problem.examples?.length > 0 && (
                    <>
                        <h3 className={styles.examplesTitle}>Examples</h3>
                        {problem.examples.map((ex, i) => (
                            <div key={i}>
                                <div className={styles.example}>
                                    <div className={styles.exampleLabel}>Input</div>
                                    <div className={styles.exampleContent}>{ex.input}</div>
                                </div>
                                <div className={styles.example}>
                                    <div className={styles.exampleLabel}>Output</div>
                                    <div className={styles.exampleContent}>{ex.output}</div>
                                </div>
                            </div>
                        ))}
                    </>
                )}
            </div>
        </div>
    );
}
