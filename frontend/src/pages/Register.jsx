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
    const [success, setSuccess] = useState(false);
    const { mutate: register, isPending, error: serverError } = useRegister();

    const errorMessage =
        clientError ||
        serverError?.response?.data?.error ||
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
        <div className="min-h-[calc(100vh-64px)] bg-bg-root flex items-center justify-center p-4 relative overflow-hidden py-16">
            {/* Background effects */}
            <div className="absolute top-1/4 right-1/4 w-[500px] h-[500px] bg-accent/10 rounded-full blur-[120px] pointer-events-none" />
            <div className="absolute bottom-1/4 left-1/4 w-[500px] h-[500px] bg-accent-secondary/10 rounded-full blur-[120px] pointer-events-none" />

            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 15 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.4 }}
                className="w-full max-w-md relative z-10"
            >
                <div className="bg-bg-elevated/90 backdrop-blur-2xl border border-border/80 rounded-3xl p-8 sm:p-10 shadow-2xl overflow-hidden relative flex flex-col gap-8">
                    {/* Top Accent Line */}
                    <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-accent via-accent-secondary to-accent" />

                    <div className="flex flex-col items-center text-center mt-2 gap-4">
                        <div className="w-16 h-16 bg-gradient-to-br from-accent/20 to-accent-secondary/20 rounded-2xl flex items-center justify-center border border-accent/30 shadow-inner">
                            <UserPlus size={32} className="text-accent" aria-hidden="true" />
                        </div>
                        <div>
                            <h1 className="text-3xl sm:text-4xl font-extrabold text-text-primary tracking-tight">
                                Join <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-accent-secondary">CodeArena</span>
                            </h1>
                            <p className="text-base text-text-secondary mt-2">
                                Create your account and start competing
                            </p>
                        </div>
                    </div>

                    {errorMessage && (
                        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="w-full flex items-center justify-center bg-red-500/10 border border-red-500/30 text-red-500 p-4 rounded-xl text-sm font-medium text-center shadow-inner">
                            {errorMessage}
                        </motion.div>
                    )}

                    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
                        <div className="flex flex-col gap-2">
                            <label className="text-sm font-semibold text-text-secondary ml-1" htmlFor="register-username">
                                Username
                            </label>
                            <div className="flex items-center w-full bg-bg-surface/50 border border-border/80 rounded-xl focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/40 transition-all shadow-inner group overflow-hidden">
                                <div className="pl-4 pr-3 flex items-center justify-center pointer-events-none">
                                    <User size={20} className="text-text-muted group-focus-within:text-accent transition-colors shrink-0" aria-hidden="true" />
                                </div>
                                <input
                                    id="register-username"
                                    className="w-full bg-transparent py-3.5 pr-4 text-base text-text-primary placeholder:text-text-muted/70 outline-none"
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

                        <div className="flex flex-col gap-2">
                            <label className="text-sm font-semibold text-text-secondary ml-1" htmlFor="register-email">
                                Email
                            </label>
                            <div className="flex items-center w-full bg-bg-surface/50 border border-border/80 rounded-xl focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/40 transition-all shadow-inner group overflow-hidden">
                                <div className="pl-4 pr-3 flex items-center justify-center pointer-events-none">
                                    <Mail size={20} className="text-text-muted group-focus-within:text-accent transition-colors shrink-0" aria-hidden="true" />
                                </div>
                                <input
                                    id="register-email"
                                    className="w-full bg-transparent py-3.5 pr-4 text-base text-text-primary placeholder:text-text-muted/70 outline-none"
                                    type="email"
                                    placeholder="you@example.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        <div className="flex flex-col gap-2">
                            <label className="text-sm font-semibold text-text-secondary ml-1" htmlFor="register-password">
                                Password
                            </label>
                            <div className="flex items-center w-full bg-bg-surface/50 border border-border/80 rounded-xl focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/40 transition-all shadow-inner group overflow-hidden">
                                <div className="pl-4 pr-3 flex items-center justify-center pointer-events-none">
                                    <Lock size={20} className="text-text-muted group-focus-within:text-accent transition-colors shrink-0" aria-hidden="true" />
                                </div>
                                <input
                                    id="register-password"
                                    className="w-full bg-transparent py-3.5 pr-4 text-base text-text-primary placeholder:text-text-muted/70 outline-none"
                                    type="password"
                                    placeholder="Min 8 chars"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    minLength={8}
                                />
                            </div>
                        </div>

                        <div className="flex flex-col gap-2">
                            <label className="text-sm font-semibold text-text-secondary ml-1" htmlFor="register-confirm">
                                Confirm Password
                            </label>
                            <div className="flex items-center w-full bg-bg-surface/50 border border-border/80 rounded-xl focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/40 transition-all shadow-inner group overflow-hidden">
                                <div className="pl-4 pr-3 flex items-center justify-center pointer-events-none">
                                    <CheckCircle2 size={20} className="text-text-muted group-focus-within:text-accent transition-colors shrink-0" aria-hidden="true" />
                                </div>
                                <input
                                    id="register-confirm"
                                    className="w-full bg-transparent py-3.5 pr-4 text-base text-text-primary placeholder:text-text-muted/70 outline-none"
                                    type="password"
                                    placeholder="Repeat password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        <div className="pt-2">
                            <Button
                                variant="primary"
                                type="submit"
                                className="w-full py-3.5 text-lg font-bold rounded-xl shadow-[0_0_20px_rgba(168,85,247,0.2)] hover:shadow-[0_0_30px_rgba(168,85,247,0.4)] transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                disabled={isPending || !username || !email || !password || !confirmPassword}
                            >
                                {isPending ? 'Creating account...' : 'Create Account'}
                                {!isPending && <ArrowRight size={22} aria-hidden="true" />}
                            </Button>
                        </div>
                    </form>

                    <div className="text-center text-sm text-text-muted font-medium pt-2">
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
