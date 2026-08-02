import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Swords, Briefcase, Zap } from 'lucide-react';
import toast from 'react-hot-toast';
import { userApi, matchmakingApi } from '../../api/auth';
import { useAuthStore } from '../../stores/authStore';

const TRACKS = [
    {
        id: 'interview',
        title: 'Interview Prep',
        desc: 'Company-style problems and timed practice.',
        icon: Briefcase,
    },
    {
        id: 'battle',
        title: '1v1 Battles',
        desc: 'Jump straight into ranked duels.',
        icon: Swords,
    },
];

export default function OnboardingModal({ onComplete }) {
    const [track, setTrack] = useState('battle');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const setUser = useAuthStore((s) => s.setUser);

    const handleStart = async (withTutorial) => {
        setLoading(true);
        try {
            const profile = await userApi.completeOnboarding({
                track,
                start_tutorial_match: withTutorial,
            });
            setUser(profile);

            if (withTutorial) {
                const res = await matchmakingApi.joinTutorial();
                if (res.match_id) {
                    navigate(`/battle/${res.match_id}`);
                }
            }
            onComplete?.();
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to complete onboarding');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[500] flex items-end sm:items-center justify-center bg-bg-root/95 backdrop-blur-sm p-0 sm:p-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-bg-primary border border-border max-w-lg w-full p-5 sm:p-8 shadow-2xl max-h-[min(92dvh,800px)] overflow-y-auto rounded-t-2xl sm:rounded-none"
            >
                <p className="editorial-kicker mb-2">Welcome to CodeArena</p>
                <h2 className="text-2xl font-bold text-text-primary mb-2">Pick your track</h2>
                <p className="text-sm text-text-secondary mb-6">
                    We&apos;ll tailor your dashboard. You can change this anytime in settings.
                </p>

                <div className="space-y-3 mb-8">
                    {TRACKS.map((t) => {
                        const Icon = t.icon;
                        const selected = track === t.id;
                        return (
                            <button
                                key={t.id}
                                type="button"
                                onClick={() => setTrack(t.id)}
                                className={`w-full flex items-start gap-4 p-4 border text-left transition-colors ${
                                    selected
                                        ? 'border-accent bg-accent/5'
                                        : 'border-border hover:border-text-muted'
                                }`}
                            >
                                <Icon size={20} className={selected ? 'text-accent' : 'text-text-muted'} />
                                <div>
                                    <div className="font-semibold text-text-primary">{t.title}</div>
                                    <div className="text-xs text-text-secondary mt-0.5">{t.desc}</div>
                                </div>
                            </button>
                        );
                    })}
                </div>

                <div className="flex flex-col gap-3">
                    <button
                        type="button"
                        disabled={loading}
                        onClick={() => handleStart(true)}
                        className="w-full flex items-center justify-center gap-2 py-3 bg-accent text-white font-semibold hover:opacity-90 disabled:opacity-50"
                    >
                        <Zap size={16} />
                        {loading ? 'Starting...' : 'Play tutorial match'}
                    </button>
                    <button
                        type="button"
                        disabled={loading}
                        onClick={() => handleStart(false)}
                        className="w-full py-2.5 border border-border text-sm font-medium text-text-secondary hover:text-text-primary hover:bg-bg-hover disabled:opacity-50"
                    >
                        Skip to dashboard
                    </button>
                </div>
            </motion.div>
        </div>
    );
}
