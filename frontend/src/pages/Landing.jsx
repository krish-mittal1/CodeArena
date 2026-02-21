import { Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import styles from '../styles/landing.module.css';

export default function Landing() {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

    return (
        <div className={styles.landing}>
            <div className={styles.content}>
                <h1 className={styles.title}>
                    Real-Time 1v1<br />
                    <span className={styles.accent}>Code Battles</span>
                </h1>
                <p className={styles.description}>
                    Compete head-to-head in timed coding challenges. Solve problems faster
                    than your opponent, climb the ELO ladder, and prove your skills.
                </p>

                <div className={styles.actions}>
                    {isAuthenticated ? (
                        <Link to="/dashboard" className={styles.primaryBtn}>
                            Go to Dashboard
                        </Link>
                    ) : (
                        <>
                            <Link to="/register" className={styles.primaryBtn}>
                                Start Competing
                            </Link>
                            <Link to="/login" className={styles.secondaryBtn}>
                                Login
                            </Link>
                        </>
                    )}
                </div>

                <div className={styles.features}>
                    <div className={styles.feature}>
                        <div className={styles.featureIcon}>⚡</div>
                        <div className={styles.featureTitle}>Real-Time Matches</div>
                        <div className={styles.featureDesc}>
                            Live WebSocket battles with instant feedback and opponent activity tracking
                        </div>
                    </div>
                    <div className={styles.feature}>
                        <div className={styles.featureIcon}>🏆</div>
                        <div className={styles.featureTitle}>ELO Rating</div>
                        <div className={styles.featureDesc}>
                            Skill-based matchmaking with dynamic ELO calculation after every match
                        </div>
                    </div>
                    <div className={styles.feature}>
                        <div className={styles.featureIcon}>🔒</div>
                        <div className={styles.featureTitle}>Secure Execution</div>
                        <div className={styles.featureDesc}>
                            Code runs in isolated Docker containers with strict resource limits
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
