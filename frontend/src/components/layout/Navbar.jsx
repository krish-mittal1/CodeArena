import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import { useBattleStore } from '../../stores/battleStore';
import { useLogout } from '../../hooks/useAuth';
import styles from './Navbar.module.css';

export default function Navbar() {
    const { user, isAuthenticated } = useAuthStore();
    const matchId = useBattleStore((s) => s.matchId);
    const handleLogout = useLogout();
    const navigate = useNavigate();

    const handleLockedNav = (path) => (e) => {
        if (matchId) {
            e.preventDefault();
            navigate(`/battle/${matchId}`);
        }
    };

    const dashboardClass = ({ isActive }) =>
        `${styles.navLink} ${isActive ? styles.active : ''} ${matchId ? styles.disabled : ''}`;

    const historyClass = ({ isActive }) =>
        `${styles.navLink} ${isActive ? styles.active : ''} ${matchId ? styles.disabled : ''}`;

    return (
        <nav className={styles.navbar}>
            <Link to="/" className={styles.logo}>
                <span className={styles.logoIcon}>⚔</span>
                <span>Code<span className={styles.accent}>Arena</span></span>
            </Link>

            {isAuthenticated && (
                <div className={styles.navLinks}>
                    <NavLink
                        to="/dashboard"
                        className={dashboardClass}
                        onClick={matchId ? handleLockedNav('/dashboard') : undefined}
                    >
                        Dashboard
                    </NavLink>
                    <NavLink
                        to="/history"
                        className={historyClass}
                        onClick={matchId ? handleLockedNav('/history') : undefined}
                    >
                        History
                    </NavLink>
                </div>
            )}

            <div className={styles.navRight}>
                {isAuthenticated ? (
                    <>
                        <div className={styles.userInfo}>
                            <span className={styles.username}>{user?.username}</span>
                            <span className={styles.eloBadge}>{user?.elo ?? '—'}</span>
                        </div>
                        <button onClick={handleLogout} className={styles.logoutBtn}>
                            Logout
                        </button>
                    </>
                ) : (
                    <div className={styles.authLinks}>
                        <Link to="/login" className={`${styles.authLink} ${styles.login}`}>
                            Login
                        </Link>
                        <Link to="/register" className={`${styles.authLink} ${styles.register}`}>
                            Register
                        </Link>
                    </div>
                )}
            </div>
        </nav>
    );
}
