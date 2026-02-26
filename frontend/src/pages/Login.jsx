import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LogIn, User, Lock, ArrowRight } from 'lucide-react';
import { useLogin } from '../hooks/useAuth';
import Button from '../components/ui/Button';

export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const { mutate: login, isPending, error } = useLogin();
    const errorMessage =
        error?.response?.data?.error || error?.response?.data?.detail || error?.message || '';

    const handleSubmit = (e) => {
        e.preventDefault();
        login({ username, password });
    };

    return (
        <div className="min-h-[calc(100vh-64px)] bg-bg-root flex items-center justify-center p-4 relative overflow-hidden">

            {/* Premium Ambient Glow Effects */}
            <div className="absolute top-1/4 right-1/4 w-[500px] h-[500px] bg-accent/10 rounded-full blur-[120px] pointer-events-none" />
            <div className="absolute bottom-1/4 left-1/4 w-[500px] h-[500px] bg-accent/8 rounded-full blur-[120px] pointer-events-none" />

            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
                className="w-full max-w-[480px] relative z-10"
            >
                <div className="bg-bg-secondary border border-border rounded-3xl p-8 sm:p-12 shadow-2xl relative">

                    {/* Header */}
                    <div className="flex flex-col items-center text-center mb-10">
                        <div className="w-16 h-16 bg-accent/10 text-accent rounded-2xl flex items-center justify-center mb-6 ring-1 ring-accent/20 shadow-[0_0_15px_var(--color-accent-glow)]">
                            <LogIn size={28} strokeWidth={2.5} aria-hidden="true" />
                        </div>
                        <h1 className="text-3xl sm:text-4xl font-extrabold text-text-primary tracking-tight">
                            Welcome Back
                        </h1>
                        <p className="text-sm sm:text-base text-text-secondary mt-3 font-medium">
                            Log in to continue your competitive coding journey
                        </p>
                    </div>

                    {/* Error Message */}
                    {errorMessage && (
                        <motion.div
                            initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                            animate={{ opacity: 1, height: 'auto', marginBottom: 24 }}
                            className="w-full flex items-center justify-center bg-loss/10 border border-loss/20 text-loss p-4 rounded-xl text-sm font-semibold text-center overflow-hidden"
                        >
                            {errorMessage}
                        </motion.div>
                    )}

                    <form onSubmit={handleSubmit} className="flex flex-col gap-6" noValidate>

                        {/* Username Input */}
                        <div className="flex flex-col gap-2">
                            <label htmlFor="login-username" className="text-sm font-semibold text-text-primary/80 ml-1">
                                Username
                            </label>
                            <div className="flex items-center w-full h-14 bg-bg-root border border-border rounded-xl focus-within:border-accent focus-within:ring-1 focus-within:ring-accent transition-all group overflow-hidden shadow-inner">
                                <div className="pl-4 pr-3 flex items-center justify-center text-text-muted group-focus-within:text-accent transition-colors shrink-0">
                                    <User size={20} strokeWidth={2.5} aria-hidden="true" />
                                </div>
                                <input
                                    id="login-username"
                                    className="flex-1 h-full bg-transparent text-base text-text-primary placeholder:text-text-muted outline-none pr-4"
                                    type="text"
                                    placeholder="Enter your username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                    autoFocus
                                />
                            </div>
                        </div>

                        {/* Password Input */}
                        <div className="flex flex-col gap-2">
                            <label htmlFor="login-password" className="text-sm font-semibold text-text-primary/80 ml-1">
                                Password
                            </label>
                            <div className="flex items-center w-full h-14 bg-bg-root border border-border rounded-xl focus-within:border-accent focus-within:ring-1 focus-within:ring-accent transition-all group overflow-hidden shadow-inner">
                                <div className="pl-4 pr-3 flex items-center justify-center text-text-muted group-focus-within:text-accent transition-colors shrink-0">
                                    <Lock size={20} strokeWidth={2.5} aria-hidden="true" />
                                </div>
                                <input
                                    id="login-password"
                                    className="flex-1 h-full bg-transparent text-base text-text-primary placeholder:text-text-muted outline-none pr-4"
                                    type="password"
                                    placeholder="Enter your password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        {/* Submit Button */}
                        <div className="pt-4">
                            <Button
                                variant="primary"
                                type="submit"
                                className="w-full h-14 text-lg font-bold rounded-xl bg-accent hover:bg-accent-hover text-white shadow-[0_0_20px_var(--color-accent-glow)] hover:shadow-[0_0_25px_var(--color-accent-glow)] transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:hover:bg-accent disabled:cursor-not-allowed border border-accent/50"
                                disabled={isPending || !username || !password}
                            >
                                {isPending ? 'Authenticating...' : 'Sign In'}
                                {!isPending && <ArrowRight size={20} strokeWidth={2.5} aria-hidden="true" />}
                            </Button>
                        </div>
                    </form>

                    {/* Footer */}
                    <div className="text-center text-sm text-text-secondary font-medium mt-8">
                        Don't have an account?{' '}
                        <Link
                            to="/register"
                            className="text-accent hover:text-accent-hover transition-colors font-bold underline decoration-accent/30 underline-offset-4 hover:decoration-accent-hover"
                        >
                            Create one now
                        </Link>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}