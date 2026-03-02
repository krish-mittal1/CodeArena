import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { UserPlus, User, Mail, Lock, CheckCircle2, ArrowRight, KeyRound, Loader2 } from 'lucide-react';
import { useRegister } from '../hooks/useAuth';
import { authApi } from '../api/auth';
import Button from '../components/ui/Button';

export default function Register() {
    const [step, setStep] = useState('form');  // 'form' | 'verify'
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [clientError, setClientError] = useState('');
    const [otpLoading, setOtpLoading] = useState(false);
    const [cooldown, setCooldown] = useState(0);

    const { mutate: register, isPending, error: serverError } = useRegister();

    const errorMessage =
        clientError ||
        serverError?.response?.data?.error ||
        serverError?.response?.data?.detail ||
        serverError?.message ||
        '';

    // Cooldown timer
    useEffect(() => {
        if (cooldown <= 0) return;
        const t = setInterval(() => setCooldown((c) => c - 1), 1000);
        return () => clearInterval(t);
    }, [cooldown]);

    // ── Step 1: Validate form and send OTP ──
    const handleSendOTP = async (e) => {
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

        setOtpLoading(true);
        try {
            await authApi.requestOTP(email);
            setStep('verify');
            setCooldown(60);
        } catch (err) {
            setClientError(
                err?.response?.data?.error ||
                err?.response?.data?.detail ||
                'Failed to send verification code. Try again.'
            );
        } finally {
            setOtpLoading(false);
        }
    };

    // ── Step 2: Verify OTP then register ──
    const handleVerifyAndRegister = async (otpString) => {
        setClientError('');
        setOtpLoading(true);
        try {
            // Verify OTP first
            await authApi.verifyOTP(email, otpString);
            // OTP valid → register the account (useRegister hook navigates on success)
            register({ username, email, password });
        } catch (err) {
            setClientError(
                err?.response?.data?.error ||
                err?.response?.data?.detail ||
                'Invalid or expired code.'
            );
        } finally {
            setOtpLoading(false);
        }
    };

    // ── Resend OTP ──
    const handleResend = async () => {
        if (cooldown > 0) return;
        setClientError('');
        setOtpLoading(true);
        try {
            await authApi.requestOTP(email);
            setCooldown(60);
        } catch (err) {
            setClientError(
                err?.response?.data?.error ||
                err?.response?.data?.detail ||
                'Failed to resend. Try again later.'
            );
        } finally {
            setOtpLoading(false);
        }
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
                            <UserPlus size={28} strokeWidth={2.5} aria-hidden="true" />
                        </div>
                        <h1 className="text-3xl sm:text-4xl font-extrabold text-text-primary tracking-tight">
                            Join <span className="text-transparent bg-clip-text bg-linear-to-r from-accent to-accent-secondary">CodeArena</span>
                        </h1>
                        <p className="text-sm sm:text-base text-text-secondary mt-3 font-medium">
                            {step === 'form' ? 'Create your account and start competing' : 'Verify your email to continue'}
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

                    <AnimatePresence mode="wait">
                        {step === 'form' ? (
                            <motion.div
                                key="form"
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 10 }}
                                transition={{ duration: 0.15 }}
                            >
                                <form onSubmit={handleSendOTP} className="flex flex-col gap-6" noValidate>

                                    {/* Username Input */}
                                    <div className="flex flex-col gap-2">
                                        <label htmlFor="register-username" className="text-sm font-semibold text-text-primary/80 ml-1">
                                            Username
                                        </label>
                                        <div className="flex items-center w-full h-14 bg-bg-root border border-border rounded-xl focus-within:border-accent focus-within:ring-1 focus-within:ring-accent transition-all group overflow-hidden shadow-inner">
                                            <div className="pl-4 pr-3 flex items-center justify-center text-text-muted group-focus-within:text-accent transition-colors shrink-0">
                                                <User size={20} strokeWidth={2.5} aria-hidden="true" />
                                            </div>
                                            <input
                                                id="register-username"
                                                className="flex-1 h-full bg-transparent text-base text-text-primary placeholder:text-text-muted outline-none pr-4"
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

                                    {/* Email Input */}
                                    <div className="flex flex-col gap-2">
                                        <label htmlFor="register-email" className="text-sm font-semibold text-text-primary/80 ml-1">
                                            Email
                                        </label>
                                        <div className="flex items-center w-full h-14 bg-bg-root border border-border rounded-xl focus-within:border-accent focus-within:ring-1 focus-within:ring-accent transition-all group overflow-hidden shadow-inner">
                                            <div className="pl-4 pr-3 flex items-center justify-center text-text-muted group-focus-within:text-accent transition-colors shrink-0">
                                                <Mail size={20} strokeWidth={2.5} aria-hidden="true" />
                                            </div>
                                            <input
                                                id="register-email"
                                                className="flex-1 h-full bg-transparent text-base text-text-primary placeholder:text-text-muted outline-none pr-4"
                                                type="email"
                                                placeholder="you@example.com"
                                                value={email}
                                                onChange={(e) => setEmail(e.target.value)}
                                                required
                                            />
                                        </div>
                                    </div>

                                    {/* Password Input */}
                                    <div className="flex flex-col gap-2">
                                        <label htmlFor="register-password" className="text-sm font-semibold text-text-primary/80 ml-1">
                                            Password
                                        </label>
                                        <div className="flex items-center w-full h-14 bg-bg-root border border-border rounded-xl focus-within:border-accent focus-within:ring-1 focus-within:ring-accent transition-all group overflow-hidden shadow-inner">
                                            <div className="pl-4 pr-3 flex items-center justify-center text-text-muted group-focus-within:text-accent transition-colors shrink-0">
                                                <Lock size={20} strokeWidth={2.5} aria-hidden="true" />
                                            </div>
                                            <input
                                                id="register-password"
                                                className="flex-1 h-full bg-transparent text-base text-text-primary placeholder:text-text-muted outline-none pr-4"
                                                type="password"
                                                placeholder="Min 8 characters"
                                                value={password}
                                                onChange={(e) => setPassword(e.target.value)}
                                                required
                                                minLength={8}
                                            />
                                        </div>
                                    </div>

                                    {/* Confirm Password Input */}
                                    <div className="flex flex-col gap-2">
                                        <label htmlFor="register-confirm" className="text-sm font-semibold text-text-primary/80 ml-1">
                                            Confirm Password
                                        </label>
                                        <div className="flex items-center w-full h-14 bg-bg-root border border-border rounded-xl focus-within:border-accent focus-within:ring-1 focus-within:ring-accent transition-all group overflow-hidden shadow-inner">
                                            <div className="pl-4 pr-3 flex items-center justify-center text-text-muted group-focus-within:text-accent transition-colors shrink-0">
                                                <CheckCircle2 size={20} strokeWidth={2.5} aria-hidden="true" />
                                            </div>
                                            <input
                                                id="register-confirm"
                                                className="flex-1 h-full bg-transparent text-base text-text-primary placeholder:text-text-muted outline-none pr-4"
                                                type="password"
                                                placeholder="Repeat password"
                                                value={confirmPassword}
                                                onChange={(e) => setConfirmPassword(e.target.value)}
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
                                            disabled={otpLoading || isPending || !username || !email || !password || !confirmPassword}
                                        >
                                            {otpLoading ? (
                                                <>
                                                    <Loader2 size={20} className="animate-spin" />
                                                    Sending verification code...
                                                </>
                                            ) : (
                                                <>
                                                    Continue
                                                    <ArrowRight size={20} strokeWidth={2.5} aria-hidden="true" />
                                                </>
                                            )}
                                        </Button>
                                    </div>
                                </form>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="verify"
                                initial={{ opacity: 0, x: 10 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -10 }}
                                transition={{ duration: 0.15 }}
                            >
                                <OTPVerifyStep
                                    email={email}
                                    isLoading={otpLoading || isPending}
                                    onVerify={handleVerifyAndRegister}
                                    onResend={handleResend}
                                    onBack={() => { setStep('form'); setClientError(''); }}
                                    cooldown={cooldown}
                                />
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Footer */}
                    <div className="text-center text-sm text-text-secondary font-medium mt-8">
                        Already have an account?{' '}
                        <Link
                            to="/login"
                            className="text-accent hover:text-accent-hover transition-colors font-bold underline decoration-accent/30 underline-offset-4 hover:decoration-accent-hover"
                        >
                            Log in instead
                        </Link>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}


/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   OTP Verify Step (reusable 6-digit input)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

function OTPVerifyStep({ email, isLoading, onVerify, onResend, onBack, cooldown }) {
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const inputRefs = useRef([]);

    const handleOtpChange = (index, value) => {
        if (!/^\d*$/.test(value)) return;
        const newOtp = [...otp];
        newOtp[index] = value.slice(-1);
        setOtp(newOtp);

        if (value && index < 5) {
            inputRefs.current[index + 1]?.focus();
        }

        const otpString = newOtp.join('');
        if (otpString.length === 6) {
            onVerify(otpString);
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
        for (let i = 0; i < 6; i++) newOtp[i] = pasted[i] || '';
        setOtp(newOtp);
        if (pasted.length === 6) onVerify(pasted);
        else inputRefs.current[pasted.length]?.focus();
    };

    return (
        <>
            <div className="flex flex-col items-center gap-2 mb-6">
                <div className="w-12 h-12 bg-accent/10 text-accent rounded-xl flex items-center justify-center ring-1 ring-accent/20">
                    <KeyRound size={22} strokeWidth={2.5} />
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
                        className="w-12 h-14 bg-bg-root border border-border rounded-xl text-center text-xl font-bold text-text-primary outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-all shadow-inner"
                        autoFocus={i === 0}
                        disabled={isLoading}
                    />
                ))}
            </div>

            {/* Loading */}
            {isLoading && (
                <div className="flex items-center justify-center gap-2 text-accent mb-4">
                    <Loader2 size={18} className="animate-spin" />
                    <span className="text-sm font-medium">Verifying...</span>
                </div>
            )}

            {/* Resend + Back */}
            <div className="flex items-center justify-between text-sm">
                <button
                    onClick={() => { onBack(); setOtp(['', '', '', '', '', '']); }}
                    className="text-text-muted hover:text-text-secondary transition-colors font-medium"
                >
                    ← Back
                </button>
                <button
                    onClick={onResend}
                    disabled={cooldown > 0 || isLoading}
                    className="text-accent hover:text-accent-hover transition-colors font-semibold disabled:text-text-muted disabled:cursor-not-allowed"
                >
                    {cooldown > 0 ? `Resend in ${cooldown}s` : 'Resend code'}
                </button>
            </div>
        </>
    );
}
