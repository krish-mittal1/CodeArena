import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import {
    User, Trophy, Target, Flame, TrendingUp, Code2, Edit3, Camera, Save, X,
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { matchApi } from '../api/auth';
import { formatWinRate, formatElo } from '../utils/formatters';
import RatingChart from '../components/dashboard/RatingChart';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { StatCardSkeleton, ChartSkeleton } from '../components/ui/Skeleton';

const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } },
};
const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 },
};

export default function Profile() {
    const user = useAuthStore((s) => s.user);
    const [bio, setBio] = useState(user?.bio || 'Competitive coder ready to battle!');
    const [editingBio, setEditingBio] = useState(false);
    const [tempBio, setTempBio] = useState(bio);

    const { data: history = [], isLoading } = useQuery({
        queryKey: ['matchHistory'],
        queryFn: matchApi.getHistory,
        enabled: !!user,
    });

    const { winCount, lossCount, drawCount } = useMemo(() => {
        let w = 0, l = 0, d = 0;
        history.forEach((m) => {
            if (m.result === 'win') w++;
            else if (m.result === 'loss') l++;
            else d++;
        });
        return { winCount: w, lossCount: l, drawCount: d };
    }, [history]);

    if (!user) return null;

    const winRate = formatWinRate(user.matches_won, user.matches_played);

    const handleSaveBio = () => {
        setBio(tempBio);
        setEditingBio(false);
    };

    const stats = [
        { label: 'ELO Rating', value: formatElo(user.elo), icon: Trophy, color: 'from-amber-500 to-orange-600' },
        { label: 'Matches', value: user.matches_played, icon: Target, color: 'from-blue-500 to-cyan-500' },
        { label: 'Wins', value: user.matches_won, icon: Flame, color: 'from-emerald-500 to-green-500' },
        { label: 'Win Rate', value: winRate, icon: TrendingUp, color: 'from-violet-500 to-purple-600' },
    ];

    return (
        <div className="min-h-screen bg-bg-root">
            <div className="max-w-[1350px] mx-auto px-8 pt-10 pb-20 w-full flex flex-col gap-6">
                {/* Profile Header */}
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
                    className="relative bg-bg-elevated/80 backdrop-blur-sm border border-border rounded-2xl p-6 md:p-8"
                >
                    <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
                        {/* Avatar */}
                        <div className="relative group shrink-0">
                            <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-2xl bg-linear-to-br from-accent to-accent-secondary flex items-center justify-center text-white text-3xl sm:text-4xl font-bold border-4 border-bg-elevated shadow-lg">
                                {user.username?.charAt(0).toUpperCase()}
                            </div>
                            <button className="absolute inset-0 rounded-2xl bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer">
                                <Camera size={20} className="text-white" />
                            </button>
                        </div>

                        {/* Info Header */}
                        <div className="flex-1 text-center sm:text-left pt-2">
                            <h1 className="text-3xl sm:text-4xl font-extrabold text-text-primary tracking-tight">{user.username}</h1>
                            <div className="flex flex-wrap items-center justify-center sm:justify-start gap-3 mt-3">
                                <Badge color="purple" className="text-sm px-3 py-1 font-semibold">{formatElo(user.elo)} ELO</Badge>
                                <span className="text-sm font-medium text-text-muted">{user.email}</span>
                            </div>

                            {/* Bio */}
                            <div className="mt-5 w-full sm:w-auto flex justify-center sm:justify-start">
                                {editingBio ? (
                                    <div className="flex items-start gap-2 w-full max-w-md">
                                        <textarea
                                            value={tempBio}
                                            onChange={(e) => setTempBio(e.target.value)}
                                            maxLength={200}
                                            rows={2}
                                            className="flex-1 bg-bg-surface border border-border rounded-xl px-4 py-3 text-sm text-text-primary resize-none focus:border-accent focus:ring-1 focus:ring-accent/30 outline-none"
                                            placeholder="Tell us about yourself..."
                                        />
                                        <div className="flex flex-col gap-2">
                                            <Button variant="primary" size="sm" onClick={handleSaveBio}><Save size={16} /></Button>
                                            <Button variant="ghost" size="sm" onClick={() => { setEditingBio(false); setTempBio(bio); }}><X size={16} /></Button>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="flex items-center gap-3 group">
                                        <p className="text-sm text-text-secondary">{bio}</p>
                                        <button onClick={() => setEditingBio(true)} className="p-1.5 rounded-lg text-text-muted hover:text-accent hover:bg-bg-hover opacity-0 group-hover:opacity-100 transition-all cursor-pointer">
                                            <Edit3 size={14} />
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </motion.div>

                {/* Stats Grid */}
                <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {isLoading
                        ? Array.from({ length: 4 }).map((_, i) => <StatCardSkeleton key={i} />)
                        : stats.map((stat) => (
                            <motion.div key={stat.label} variants={item}>
                                <div className="bg-bg-elevated/80 border border-border rounded-2xl p-6 hover:bg-bg-hover transition-colors flex items-center gap-4">
                                    <div className={`w-12 h-12 rounded-xl bg-linear-to-br ${stat.color} flex items-center justify-center shadow-lg shrink-0`}>
                                        <stat.icon size={22} className="text-white" />
                                    </div>
                                    <div>
                                        <p className="text-[11px] text-text-muted uppercase tracking-widest font-semibold mb-1">{stat.label}</p>
                                        <p className="text-2xl font-bold text-text-primary tracking-tight leading-none">{stat.value}</p>
                                    </div>
                                </div>
                            </motion.div>
                        ))
                    }
                </motion.div>

                {/* Rating Chart */}
                <div className="h-[400px] w-full bg-bg-elevated/80 border border-border rounded-2xl p-6 mt-2">
                    {isLoading ? <ChartSkeleton /> : <RatingChart history={history} currentElo={user.elo} />}
                </div>

                {/* Match Breakdown */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="bg-bg-elevated/80 border border-border rounded-2xl p-8 mt-2"
                >
                    <h3 className="text-lg font-semibold text-text-primary flex items-center gap-2 mb-6">
                        <Code2 size={18} className="text-accent" />
                        Match Breakdown
                    </h3>

                    {history.length === 0 ? (
                        <p className="text-sm text-text-muted text-center py-6">No match data yet. Play some matches!</p>
                    ) : (
                        <div className="space-y-4">
                            {[
                                { label: 'Wins', count: winCount, total: history.length, color: 'from-emerald-500 to-green-500' },
                                { label: 'Losses', count: lossCount, total: history.length, color: 'from-red-500 to-rose-500' },
                                { label: 'Draws', count: drawCount, total: history.length, color: 'from-amber-500 to-yellow-500' },
                            ].map(({ label, count, total, color }) => {
                                const pct = total > 0 ? Math.round((count / total) * 100) : 0;
                                return (
                                    <div key={label}>
                                        <div className="flex items-center justify-between mb-1.5">
                                            <span className="text-sm font-medium text-text-primary">{label}</span>
                                            <span className="text-xs text-text-muted">{count} matches · {pct}%</span>
                                        </div>
                                        <div className="w-full h-2.5 bg-bg-surface rounded-full overflow-hidden">
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: `${pct}%` }}
                                                transition={{ duration: 0.8, delay: 0.1 }}
                                                className={`h-full bg-linear-to-r ${color} rounded-full`}
                                            />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </motion.div>
            </div>
        </div>
    );
}
