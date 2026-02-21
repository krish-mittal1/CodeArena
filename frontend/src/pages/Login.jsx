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
        <div className="min-h-[calc(100vh-64px)] bg-[#09090b] flex items-center justify-center p-4 relative overflow-hidden">

            {/* Premium Ambient Glow Effects */}
            <div className="absolute top-1/4 right-1/4 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none" />
            <div className="absolute bottom-1/4 left-1/4 w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none" />

            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
                className="w-full max-w-[480px] relative z-10"
            >
                {/* Solid, high-contrast card background instead of muddy translucency.
                    Subtle border and shadow for depth. 
                */}
                <div className="bg-[#121217] border border-white/10 rounded-3xl p-8 sm:p-12 shadow-2xl relative">

                    {/* Header */}
                    <div className="flex flex-col items-center text-center mb-10">
                        <div className="w-16 h-16 bg-purple-500/10 text-purple-500 rounded-2xl flex items-center justify-center mb-6 ring-1 ring-purple-500/20 shadow-[0_0_15px_rgba(168,85,247,0.15)]">
                            <LogIn size={28} strokeWidth={2.5} aria-hidden="true" />
                        </div>
                        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                            Welcome Back
                        </h1>
                        <p className="text-sm sm:text-base text-zinc-400 mt-3 font-medium">
                            Log in to continue your competitive coding journey
                        </p>
                    </div>

                    {/* Error Message */}
                    {errorMessage && (
                        <motion.div
                            initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                            animate={{ opacity: 1, height: 'auto', marginBottom: 24 }}
                            className="w-full flex items-center justify-center bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm font-semibold text-center overflow-hidden"
                        >
                            {errorMessage}
                        </motion.div>
                    )}

                    {/* Added noValidate to KILL the ugly native browser tooltips */}
                    <form onSubmit={handleSubmit} className="flex flex-col gap-6" noValidate>

                        {/* Username Input */}
                        <div className="flex flex-col gap-2">
                            <label htmlFor="login-username" className="text-sm font-semibold text-zinc-300 ml-1">
                                Username
                            </label>
                            {/* Fixed height (h-14) ensures it never squishes */}
                            <div className="flex items-center w-full h-14 bg-[#09090b] border border-white/10 rounded-xl focus-within:border-purple-500 focus-within:ring-1 focus-within:ring-purple-500 transition-all group overflow-hidden shadow-inner">
                                <div className="pl-4 pr-3 flex items-center justify-center text-zinc-500 group-focus-within:text-purple-400 transition-colors shrink-0">
                                    <User size={20} strokeWidth={2.5} aria-hidden="true" />
                                </div>
                                <input
                                    id="login-username"
                                    className="flex-1 h-full bg-transparent text-base text-white placeholder:text-zinc-600 outline-none pr-4"
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
                            <label htmlFor="login-password" className="text-sm font-semibold text-zinc-300 ml-1">
                                Password
                            </label>
                            <div className="flex items-center w-full h-14 bg-[#09090b] border border-white/10 rounded-xl focus-within:border-purple-500 focus-within:ring-1 focus-within:ring-purple-500 transition-all group overflow-hidden shadow-inner">
                                <div className="pl-4 pr-3 flex items-center justify-center text-zinc-500 group-focus-within:text-purple-400 transition-colors shrink-0">
                                    <Lock size={20} strokeWidth={2.5} aria-hidden="true" />
                                </div>
                                <input
                                    id="login-password"
                                    className="flex-1 h-full bg-transparent text-base text-white placeholder:text-zinc-600 outline-none pr-4"
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
                                className="w-full h-14 text-lg font-bold rounded-xl bg-purple-600 hover:bg-purple-500 text-white shadow-[0_0_20px_rgba(168,85,247,0.15)] hover:shadow-[0_0_25px_rgba(168,85,247,0.3)] transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:hover:bg-purple-600 disabled:cursor-not-allowed border border-purple-500/50"
                                disabled={isPending || !username || !password}
                            >
                                {isPending ? 'Authenticating...' : 'Sign In'}
                                {!isPending && <ArrowRight size={20} strokeWidth={2.5} aria-hidden="true" />}
                            </Button>
                        </div>
                    </form>

                    {/* Footer */}
                    <div className="text-center text-sm text-zinc-400 font-medium mt-8">
                        Don't have an account?{' '}
                        <Link
                            to="/register"
                            className="text-purple-400 hover:text-purple-300 transition-colors font-bold underline decoration-purple-400/30 underline-offset-4 hover:decoration-purple-300"
                        >
                            Create one now
                        </Link>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}