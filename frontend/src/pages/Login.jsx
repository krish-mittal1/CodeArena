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
        error?.response?.data?.detail || error?.message || '';

    const handleSubmit = (e) => {
        e.preventDefault();
        login({ username, password });
    };

    return (
        <div className="min-h-[calc(100vh-64px)] bg-bg-root flex items-center justify-center p-4 relative overflow-hidden">
            {/* Background effects */}
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-accent/10 rounded-full blur-[100px] pointer-events-none" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-secondary/10 rounded-full blur-[100px] pointer-events-none" />

            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="w-full max-w-md relative z-10"
            >
                <div className="bg-bg-elevated/80 backdrop-blur-xl border border-border rounded-3xl p-8 sm:p-10 shadow-2xl shadow-black/50 overflow-hidden relative">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-accent to-accent-secondary" />

                    <div className="mb-8 text-center">
                        <div className="w-16 h-16 bg-gradient-to-br from-accent/20 to-accent-secondary/20 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-accent/20 shadow-inner">
                            <LogIn size={28} className="text-accent" />
                        </div>
                        <h1 className="text-3xl font-extrabold text-text-primary tracking-tight">
                            Welcome <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-accent-secondary">Back</span>
                        </h1>
                        <p className="text-text-secondary mt-2 text-sm">
                            Log in to continue your competitive coding journey
                        </p>
                    </div>

                    {errorMessage && (
                        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-xl text-sm font-medium mb-6 text-center shadow-inner">
                            {errorMessage}
                        </motion.div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div className="space-y-1.5">
                            <label className="text-sm font-semibold text-text-secondary ml-1" htmlFor="login-username">
                                Username
                            </label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-text-muted group-focus-within:text-accent transition-colors">
                                    <User size={18} />
                                </div>
                                <input
                                    id="login-username"
                                    className="w-full bg-bg-surface/50 border border-border rounded-xl pl-11 pr-4 py-3.5 text-text-primary placeholder:text-text-muted focus:border-accent focus:ring-1 focus:ring-accent/30 outline-none transition-all"
                                    type="text"
                                    placeholder="Enter your username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                    autoFocus
                                />
                            </div>
                        </div>

                        <div className="space-y-1.5">
                            <label className="text-sm font-semibold text-text-secondary ml-1" htmlFor="login-password">
                                Password
                            </label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-text-muted group-focus-within:text-accent transition-colors">
                                    <Lock size={18} />
                                </div>
                                <input
                                    id="login-password"
                                    className="w-full bg-bg-surface/50 border border-border rounded-xl pl-11 pr-4 py-3.5 text-text-primary placeholder:text-text-muted focus:border-accent focus:ring-1 focus:ring-accent/30 outline-none transition-all"
                                    type="password"
                                    placeholder="Enter your password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        <Button
                            variant="primary"
                            type="submit"
                            className="w-full py-4 text-base font-bold shadow-accent-glow/20 mt-2"
                            disabled={isPending || !username || !password}
                        >
                            <div className="flex items-center justify-center gap-2">
                                {isPending ? 'Authenticating...' : 'Sign In'}
                                {!isPending && <ArrowRight size={18} />}
                            </div>
                        </Button>
                    </form>

                    <div className="mt-8 text-center text-sm text-text-muted font-medium">
                        Don't have an account?{' '}
                        <Link to="/register" className="text-accent hover:text-accent-hover hover:underline transition-colors font-semibold">
                            Create one now
                        </Link>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
