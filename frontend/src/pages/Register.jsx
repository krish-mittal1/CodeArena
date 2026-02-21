import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { UserPlus, User, Mail, Lock, CheckCircle2, ArrowRight } from 'lucide-react';
import { useRegister } from '../hooks/useAuth';
import Button from '../components/ui/Button';

export default function Register() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [clientError, setClientError] = useState('');
    const { mutate: register, isPending, error: serverError } = useRegister();

    const errorMessage =
        clientError ||
        serverError?.response?.data?.detail ||
        serverError?.message ||
        '';

    const handleSubmit = (e) => {
        e.preventDefault();
        setClientError('');

        if (password !== confirmPassword) {
            setClientError('Passwords do not match');
            return;
        }
        if (password.length < 8) {
            setClientError('Password must be at least 8 characters');
            return;
        }

        register({ username, email, password });
    };

    return (
        <div className="min-h-[calc(100vh-64px)] bg-bg-root flex items-center justify-center p-4 relative overflow-hidden py-12">
            {/* Background effects */}
            <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-accent/10 rounded-full blur-[100px] pointer-events-none" />
            <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-accent-secondary/10 rounded-full blur-[100px] pointer-events-none" />

            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="w-full max-w-[480px] relative z-10"
            >
                <div className="bg-bg-elevated/80 backdrop-blur-xl border border-border rounded-3xl p-8 sm:p-10 shadow-2xl shadow-black/50 overflow-hidden relative">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-accent to-accent-secondary" />

                    <div className="mb-8 text-center">
                        <div className="w-16 h-16 bg-gradient-to-br from-accent/20 to-accent-secondary/20 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-accent/20 shadow-inner">
                            <UserPlus size={28} className="text-accent" />
                        </div>
                        <h1 className="text-3xl font-extrabold text-text-primary tracking-tight">
                            Join <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-accent-secondary">CodeArena</span>
                        </h1>
                        <p className="text-text-secondary mt-2 text-sm">
                            Create your account and start competing
                        </p>
                    </div>

                    {errorMessage && (
                        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-xl text-sm font-medium mb-6 text-center shadow-inner">
                            {errorMessage}
                        </motion.div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-1.5">
                            <label className="text-sm font-semibold text-text-secondary ml-1" htmlFor="register-username">
                                Username
                            </label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-text-muted group-focus-within:text-accent transition-colors">
                                    <User size={18} />
                                </div>
                                <input
                                    id="register-username"
                                    className="w-full bg-bg-surface/50 border border-border rounded-xl pl-11 pr-4 py-3 text-text-primary placeholder:text-text-muted focus:border-accent focus:ring-1 focus:ring-accent/30 outline-none transition-all"
                                    type="text"
                                    placeholder="Choose a username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                    autoFocus
                                    minLength={3}
                                    maxLength={50}
                                />
                            </div>
                        </div>

                        <div className="space-y-1.5">
                            <label className="text-sm font-semibold text-text-secondary ml-1" htmlFor="register-email">
                                Email
                            </label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-text-muted group-focus-within:text-accent transition-colors">
                                    <Mail size={18} />
                                </div>
                                <input
                                    id="register-email"
                                    className="w-full bg-bg-surface/50 border border-border rounded-xl pl-11 pr-4 py-3 text-text-primary placeholder:text-text-muted focus:border-accent focus:ring-1 focus:ring-accent/30 outline-none transition-all"
                                    type="email"
                                    placeholder="you@example.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div className="space-y-1.5">
                                <label className="text-sm font-semibold text-text-secondary ml-1" htmlFor="register-password">
                                    Password
                                </label>
                                <div className="relative group">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-text-muted group-focus-within:text-accent transition-colors">
                                        <Lock size={18} />
                                    </div>
                                    <input
                                        id="register-password"
                                        className="w-full bg-bg-surface/50 border border-border rounded-xl pl-11 pr-4 py-3 text-text-primary placeholder:text-text-muted focus:border-accent focus:ring-1 focus:ring-accent/30 outline-none transition-all"
                                        type="password"
                                        placeholder="Min 8 chars"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                        minLength={8}
                                    />
                                </div>
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-sm font-semibold text-text-secondary ml-1" htmlFor="register-confirm">
                                    Confirm <span className="hidden sm:inline">Password</span>
                                </label>
                                <div className="relative group">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-text-muted group-focus-within:text-accent transition-colors">
                                        <CheckCircle2 size={18} />
                                    </div>
                                    <input
                                        id="register-confirm"
                                        className="w-full bg-bg-surface/50 border border-border rounded-xl pl-11 pr-4 py-3 text-text-primary placeholder:text-text-muted focus:border-accent focus:ring-1 focus:ring-accent/30 outline-none transition-all"
                                        type="password"
                                        placeholder="Repeat password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>
                        </div>

                        <Button
                            variant="primary"
                            type="submit"
                            className="w-full py-4 text-base font-bold shadow-accent-glow/20 mt-4"
                            disabled={isPending || !username || !email || !password || !confirmPassword}
                        >
                            <div className="flex items-center justify-center gap-2">
                                {isPending ? 'Creating account...' : 'Create Account'}
                                {!isPending && <ArrowRight size={18} />}
                            </div>
                        </Button>
                    </form>

                    <div className="mt-8 text-center text-sm text-text-muted font-medium">
                        Already have an account?{' '}
                        <Link to="/login" className="text-accent hover:text-accent-hover hover:underline transition-colors font-semibold">
                            Log in instead
                        </Link>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
