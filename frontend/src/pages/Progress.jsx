import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Target, TrendingUp, AlertTriangle, Building2 } from 'lucide-react';
import { userApi } from '../api/auth';

function Bar({ pct, color = 'bg-accent' }) {
    return (
        <div className="h-2 bg-bg-surface rounded-full overflow-hidden">
            <div className={`h-full ${color} transition-all`} style={{ width: `${Math.min(100, pct)}%` }} />
        </div>
    );
}

export default function Progress() {
    const navigate = useNavigate();
    const { data, isLoading, isError } = useQuery({
        queryKey: ['userProgress'],
        queryFn: userApi.getProgress,
    });

    if (isLoading) {
        return <div className="min-h-screen bg-bg-root flex items-center justify-center text-text-secondary text-sm">Loading progress...</div>;
    }
    if (isError || !data) {
        return <div className="min-h-screen bg-bg-root flex items-center justify-center text-loss text-sm">Failed to load progress</div>;
    }

    return (
        <div className="min-h-screen bg-bg-root pb-16">
            <div className="max-w-4xl mx-auto px-6 py-10">
                <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
                    <p className="editorial-kicker mb-1">Interview readiness</p>
                    <h1 className="text-2xl font-bold text-text-primary">Your Progress</h1>
                    <p className="text-sm text-text-secondary mt-2">
                        {data.total_solved} / {data.total_problems} DSA problems solved
                    </p>
                </motion.div>

                {data.weak_topics?.length > 0 && (
                    <div className="paper-card grain-panel p-5 mb-6 border-l-4 border-loss">
                        <div className="flex items-center gap-2 mb-3">
                            <AlertTriangle size={18} className="text-loss" />
                            <h2 className="font-semibold text-text-primary">Weak topics</h2>
                        </div>
                        <ul className="space-y-2 text-sm">
                            {data.weak_topics.map((w) => (
                                <li key={w.topic} className="flex justify-between text-text-secondary">
                                    <span>{w.topic}</span>
                                    <span>{w.fail_rate_pct}% fail rate · {w.solved}/{w.total} solved</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                <div className="grid gap-6 md:grid-cols-2">
                    <div className="paper-card grain-panel p-5">
                        <div className="flex items-center gap-2 mb-4">
                            <TrendingUp size={18} className="text-accent" />
                            <h2 className="font-semibold">By topic</h2>
                        </div>
                        <ul className="space-y-4">
                            {data.topics?.map((t) => (
                                <li key={t.topic}>
                                    <div className="flex justify-between text-sm mb-1">
                                        <button
                                            type="button"
                                            className="text-text-primary hover:text-accent"
                                            onClick={() => navigate(`/practice/dsa/topics?topic=${encodeURIComponent(t.topic)}`)}
                                        >
                                            {t.topic}
                                        </button>
                                        <span className="text-text-muted">{t.solved}/{t.total}</span>
                                    </div>
                                    <Bar pct={t.readiness_pct} />
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className="paper-card grain-panel p-5">
                        <div className="flex items-center gap-2 mb-4">
                            <Building2 size={18} className="text-accent" />
                            <h2 className="font-semibold">Company readiness</h2>
                        </div>
                        <ul className="space-y-4 max-h-[480px] overflow-y-auto">
                            {data.companies?.slice(0, 12).map((c) => (
                                <li key={c.company}>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-text-primary">{c.company}</span>
                                        <span className="text-text-muted">{c.readiness_pct}%</span>
                                    </div>
                                    <Bar pct={c.readiness_pct} color="bg-win/80" />
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                <button
                    type="button"
                    onClick={() => navigate('/study-paths')}
                    className="mt-8 flex items-center gap-2 text-accent text-sm font-medium hover:underline"
                >
                    <Target size={16} />
                    View study paths
                </button>
            </div>
        </div>
    );
}
