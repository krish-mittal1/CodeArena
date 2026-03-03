import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { LogIn, User, Lock, ArrowRight, Mail, KeyRound, Loader2 } from 'lucide-react';
import { useLogin } from '../hooks/useAuth';
import { useAuthStore } from '../stores/authStore';
import { authApi } from '../api/auth';
import Button from '../components/ui/Button';

export default function Login() {
    const [tab, setTab] = useState('password'); // 'password' | 'otp'

    return (
        <div className="min-h-[calc(100vh-64px)] bg-bg-root flex items-center justify-center p-4">

            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
                className="w-full max-w-[480px]"
            >
                <div className="bg-bg-secondary border border-border rounded-xl p-8 sm:p-12">

                    {/* Header */}
                    <div className="flex flex-col items-center text-center mb-8">
                        <div className="w-14 h-14 bg-accent/10 text-accent rounded-xl flex items-center justify-center mb-5 border border-accent/20">
                            <LogIn size={26} strokeWidth={2.5} aria-hidden="true" />
                        </div>
                        <h1 className="text-3xl sm:text-4xl font-extrabold text-text-primary tracking-tight">
                            Welcome Back
                        </h1>
                        <p className="text-sm sm:text-base text-text-secondary mt-3 font-medium">
                            Log in to continue your competitive coding journey
                        </p>
                    </div>

                    {/* Tab Switcher */}
                    <div className="flex bg-bg-root rounded-lg p-1 mb-8 border border-border">
                        <button
                            onClick={() => setTab('password')}
                            className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-md text-sm font-semibold transition-colors duration-200 ${tab === 'password'
                                ? 'bg-bg-secondary text-text-primary border border-border'
                                : 'text-text-muted hover:text-text-secondary'
                                }`}
                        >
                            <Lock size={16} strokeWidth={2.5} />
                            Password
                        </button>
                        <button
                            onClick={() => setTab('otp')}
                            className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-md text-sm font-semibold transition-colors duration-200 ${tab === 'otp'
                                ? 'bg-bg-secondary text-text-primary border border-border'
                                : 'text-text-muted hover:text-text-secondary'
                                }`}
                        >
                            <Mail size={16} strokeWidth={2.5} />
                            Email OTP
                        </button>
                    </div>

                    {/* Tab Content */}
                    <AnimatePresence mode="wait">
                        {tab === 'password' ? (
                            <motion.div
                                key="password"
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 10 }}
                                transition={{ duration: 0.15 }}
                            >
                                <PasswordForm />
                            </motion.div>
                        ) : (
                            <motion.div
                                key="otp"
                                initial={{ opacity: 0, x: 10 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -10 }}
                                transition={{ duration: 0.15 }}
                            >
                                <OTPForm />
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Footer */}
                    <div className="text-center text-sm text-text-secondary font-medium mt-8">
                        Don't have an account?{' '}
                        <Link
                            to="/register"
                            className="text-accent hover:text-accent-hover transition-colors font-bold underline underline-offset-4"
                        >
                            Create one now
                        </Link>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}


/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Password Form (existing login flow)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

function PasswordForm() {
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
        <>
            {errorMessage && (
                <motion.div
                    initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                    animate={{ opacity: 1, height: 'auto', marginBottom: 24 }}
                    className="w-full flex items-center justify-center bg-loss/10 border border-loss/20 text-loss p-4 rounded-lg text-sm font-semibold text-center overflow-hidden"
                >
                    {errorMessage}
                </motion.div>
            )}

            <form onSubmit={handleSubmit} className="flex flex-col gap-5" noValidate>
                {/* Username Input */}
                <div className="flex flex-col gap-2">
                    <label htmlFor="login-username" className="text-sm font-semibold text-text-primary/80 ml-1">
                        Username
                    </label>
                    <div className="flex items-center w-full h-12 bg-bg-root border border-border rounded-lg focus-within:border-accent transition-colors group overflow-hidden">
                        <div className="pl-4 pr-3 flex items-center justify-center text-text-muted group-focus-within:text-accent transition-colors shrink-0">
                            <User size={18} strokeWidth={2.5} aria-hidden="true" />
                        </div>
                        <input
                            id="login-username"
                            className="flex-1 h-full bg-transparent text-sm text-text-primary placeholder:text-text-muted outline-none pr-4"
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
                    <div className="flex items-center w-full h-12 bg-bg-root border border-border rounded-lg focus-within:border-accent transition-colors group overflow-hidden">
                        <div className="pl-4 pr-3 flex items-center justify-center text-text-muted group-focus-within:text-accent transition-colors shrink-0">
                            <Lock size={18} strokeWidth={2.5} aria-hidden="true" />
                        </div>
                        <input
                            id="login-password"
                            className="flex-1 h-full bg-transparent text-sm text-text-primary placeholder:text-text-muted outline-none pr-4"
                            type="password"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                </div>

                {/* Submit Button */}
                <div className="pt-3">
                    <Button
                        variant="primary"
                        type="submit"
                        className="w-full h-12 text-base font-bold rounded-lg bg-accent hover:bg-accent-hover text-white transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={isPending || !username || !password}
                    >
                        {isPending ? 'Authenticating...' : 'Sign In'}
                        {!isPending && <ArrowRight size={18} strokeWidth={2.5} aria-hidden="true" />}
                    </Button>
                </div>
            </form>
        </>
    );
}


/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   OTP Form (new email OTP login flow)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

function OTPForm() {
    const navigate = useNavigate();
    const { _handleTokens } = useAuthStore();

    const [step, setStep] = useState('email');       // 'email' | 'verify'
    const [email, setEmail] = useState('');
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [successMsg, setSuccessMsg] = useState('');
    const [cooldown, setCooldown] = useState(0);

    const inputRefs = useRef([]);

    // Cooldown timer
    useEffect(() => {
        if (cooldown <= 0) return;
        const t = setInterval(() => setCooldown((c) => c - 1), 1000);
        return () => clearInterval(t);
    }, [cooldown]);

    // ── Step 1: Request OTP ──────────────────────────
    const handleRequestOTP = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const res = await authApi.requestOTP(email);
            setSuccessMsg(res.message || 'Verification code sent!');
            setStep('verify');
            setCooldown(60);
        } catch (err) {
            setError(
                err?.response?.data?.error ||
                err?.response?.data?.detail ||
                'Failed to send OTP. Please try again.'
            );
        } finally {
            setIsLoading(false);
        }
    };

    // ── Step 2: Verify OTP ───────────────────────────
    const handleVerifyOTP = async (otpString) => {
        setError('');
        setIsLoading(true);

        try {
            const tokens = await authApi.verifyOTP(email, otpString);
            await _handleTokens(tokens);
            navigate('/dashboard', { replace: true });
        } catch (err) {
            setError(
                err?.response?.data?.error ||
                err?.response?.data?.detail ||
                'Invalid or expired OTP.'
            );
            setOtp(['', '', '', '', '', '']);
            inputRefs.current[0]?.focus();
        } finally {
            setIsLoading(false);
        }
    };

    // ── Resend OTP ───────────────────────────────────
    const handleResend = async () => {
        if (cooldown > 0) return;
        setError('');
        setIsLoading(true);

        try {
            await authApi.requestOTP(email);
            setSuccessMsg('New code sent!');
            setCooldown(60);
            setOtp(['', '', '', '', '', '']);
        } catch (err) {
            setError(
                err?.response?.data?.error ||
                err?.response?.data?.detail ||
                'Failed to resend. Try again later.'
            );
        } finally {
            setIsLoading(false);
        }
    };

    // ── OTP digit input handler ──────────────────────
    const handleOtpChange = (index, value) => {
        if (!/^\d*$/.test(value)) return;

        const newOtp = [...otp];
        newOtp[index] = value.slice(-1);
        setOtp(newOtp);

        // Auto-advance
        if (value && index < 5) {
            inputRefs.current[index + 1]?.focus();
        }

        // Auto-submit when all 6 digits entered
        const otpString = newOtp.join('');
        if (otpString.length === 6) {
            handleVerifyOTP(otpString);
        }
    };

    const handleOtpKeyDown = (index, e) => {
        if (e.key === 'Backspace' && !otp[index] && index > 0) {
            inputRefs.current[index - 1]?.focus();
        }
    };

    const handleOtpPaste = (e) => {
        e.preventDefault();
        const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
        if (!pasted) return;

        const newOtp = [...otp];
        for (let i = 0; i < 6; i++) {
            newOtp[i] = pasted[i] || '';
        }
        setOtp(newOtp);

        if (pasted.length === 6) {
            handleVerifyOTP(pasted);
        } else {
            inputRefs.current[pasted.length]?.focus();
        }
    };

    // ── Email Step ───────────────────────────────────
    if (step === 'email') {
        return (
            <>
                {error && (
                    <motion.div
                        initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                        animate={{ opacity: 1, height: 'auto', marginBottom: 24 }}
                        className="w-full flex items-center justify-center bg-loss/10 border border-loss/20 text-loss p-4 rounded-lg text-sm font-semibold text-center overflow-hidden"
                    >
                        {error}
                    </motion.div>
                )}

                <form onSubmit={handleRequestOTP} className="flex flex-col gap-5" noValidate>
                    <div className="flex flex-col gap-2">
                        <label htmlFor="otp-email" className="text-sm font-semibold text-text-primary/80 ml-1">
                            Email Address
                        </label>
                        <div className="flex items-center w-full h-12 bg-bg-root border border-border rounded-lg focus-within:border-accent transition-colors group overflow-hidden">
                            <div className="pl-4 pr-3 flex items-center justify-center text-text-muted group-focus-within:text-accent transition-colors shrink-0">
                                <Mail size={18} strokeWidth={2.5} aria-hidden="true" />
                            </div>
                            <input
                                id="otp-email"
                                className="flex-1 h-full bg-transparent text-sm text-text-primary placeholder:text-text-muted outline-none pr-4"
                                type="email"
                                placeholder="you@example.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                autoFocus
                            />
                        </div>
                    </div>

                    <div className="pt-3">
                        <Button
                            variant="primary"
                            type="submit"
                            className="w-full h-12 text-base font-bold rounded-lg bg-accent hover:bg-accent-hover text-white transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                            disabled={isLoading || !email}
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 size={18} className="animate-spin" />
                                    Sending...
                                </>
                            ) : (
                                <>
                                    Send Verification Code
                                    <ArrowRight size={18} strokeWidth={2.5} aria-hidden="true" />
                                </>
                            )}
                        </Button>
                    </div>
                </form>

                <p className="text-xs text-text-muted text-center mt-4">
                    We'll send a 6-digit code to your email. No password needed.
                </p>
            </>
        );
    }

    // ── Verify Step ──────────────────────────────────
    return (
        <>
            {error && (
                <motion.div
                    initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                    animate={{ opacity: 1, height: 'auto', marginBottom: 24 }}
                    className="w-full flex items-center justify-center bg-loss/10 border border-loss/20 text-loss p-4 rounded-lg text-sm font-semibold text-center overflow-hidden"
                >
                    {error}
                </motion.div>
            )}

            {successMsg && (
                <motion.div
                    initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                    animate={{ opacity: 1, height: 'auto', marginBottom: 24 }}
                    className="w-full flex items-center justify-center bg-win/10 border border-win/20 text-win p-4 rounded-lg text-sm font-semibold text-center overflow-hidden"
                >
                    {successMsg}
                </motion.div>
            )}

            <div className="flex flex-col items-center gap-2 mb-6">
                <div className="w-11 h-11 bg-accent/10 text-accent rounded-lg flex items-center justify-center border border-accent/20">
                    <KeyRound size={20} strokeWidth={2.5} />
                </div>
                <p className="text-sm text-text-secondary text-center">
                    Enter the 6-digit code sent to
                </p>
                <p className="text-sm text-text-primary font-bold">{email}</p>
            </div>

            {/* OTP Input Boxes */}
            <div className="flex justify-center gap-3 mb-8" onPaste={handleOtpPaste}>
                {otp.map((digit, i) => (
                    <input
                        key={i}
                        ref={(el) => (inputRefs.current[i] = el)}
                        type="text"
                        inputMode="numeric"
                        maxLength={1}
                        value={digit}
                        onChange={(e) => handleOtpChange(i, e.target.value)}
                        onKeyDown={(e) => handleOtpKeyDown(i, e)}
                        className="w-11 h-13 bg-bg-root border border-border rounded-lg text-center text-xl font-bold text-text-primary outline-none focus:border-accent transition-colors"
                        autoFocus={i === 0}
                        disabled={isLoading}
                    />
                ))}
            </div>

            {/* Loading indicator */}
            {isLoading && (
                <div className="flex items-center justify-center gap-2 text-accent mb-4">
                    <Loader2 size={18} className="animate-spin" />
                    <span className="text-sm font-medium">Verifying...</span>
                </div>
            )}

            {/* Resend + Back */}
            <div className="flex items-center justify-between text-sm">
                <button
                    onClick={() => { setStep('email'); setError(''); setSuccessMsg(''); setOtp(['', '', '', '', '', '']); }}
                    className="text-text-muted hover:text-text-secondary transition-colors font-medium"
                >
                    ← Change email
                </button>
                <button
                    onClick={handleResend}
                    disabled={cooldown > 0 || isLoading}
                    className="text-accent hover:text-accent-hover transition-colors font-semibold disabled:text-text-muted disabled:cursor-not-allowed"
                >
                    {cooldown > 0 ? `Resend in ${cooldown}s` : 'Resend code'}
                </button>
            </div>
        </>
    );
}