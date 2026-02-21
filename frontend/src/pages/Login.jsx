import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useLogin } from '../hooks/useAuth';
import styles from '../styles/auth.module.css';

export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const { mutate: login, isPending, error } = useLogin();

    const errorMessage =
        error?.response?.data?.detail || error?.message || '';

    const handleSubmit = (e) => {
        e.preventDefault();
        login({ username, password });
    };

    return (
        <div className={styles.authPage}>
            <div className={styles.authCard}>
                <h1 className={styles.authTitle}>
                    Welcome <span className={styles.accent}>back</span>
                </h1>
                <p className={styles.authSubtitle}>
                    Log in to continue your competitive coding journey
                </p>

                {errorMessage && <div className={styles.error}>{errorMessage}</div>}

                <form onSubmit={handleSubmit}>
                    <div className={styles.formGroup}>
                        <label className={styles.label} htmlFor="login-username">
                            Username
                        </label>
                        <input
                            id="login-username"
                            className={styles.input}
                            type="text"
                            placeholder="Enter your username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            autoFocus
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label className={styles.label} htmlFor="login-password">
                            Password
                        </label>
                        <input
                            id="login-password"
                            className={styles.input}
                            type="password"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className={styles.submitBtn}
                        disabled={isPending || !username || !password}
                    >
                        {isPending ? 'Logging in...' : 'Login'}
                    </button>
                </form>

                <p className={styles.footer}>
                    Don't have an account? <Link to="/register">Register</Link>
                </p>
            </div>
        </div>
    );
}
