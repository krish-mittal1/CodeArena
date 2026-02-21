import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
    Trophy, Target, Flame, TrendingUp, Swords, Clock, ChevronRight,
} from 'lucide-react';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import { useAuthStore } from '../stores/authStore';
import { useBattleStore } from '../stores/battleStore';
import { useMatchmakingStore } from '../stores/matchmakingStore';
import { matchApi } from '../api/auth';
import { formatWinRate, formatElo } from '../utils/formatters';
import QueueOverlay from '../components/matchmaking/QueueOverlay';
import RatingChart from '../components/dashboard/RatingChart';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { StatCardSkeleton, ChartSkeleton } from '../components/ui/Skeleton';

dayjs.extend(relativeTime);

export default function Dashboard() {
    const user = useAuthStore((s) => s.user);
    const queueStatus = useMatchmakingStore((s) => s.status);
    const joinQueue = useMatchmakingStore((s) => s.joinQueue);
    const leaveQueue = useMatchmakingStore((s) => s.leaveQueue);
    const resetQueue = useMatchmakingStore((s) => s.reset);
    const matchId = useBattleStore((s) => s.matchId);
    const hasInitializedRef = useRef(false);
    const navigate = useNavigate();

    const { data: history, isLoading: historyLoading, isError } = useQuery({
        queryKey: ['matchHistory'],
        queryFn: matchApi.getHistory,
        enabled: !!user,
    });

    useEffect(() => {
        if (hasInitializedRef.current) return;
        hasInitializedRef.current = true;
        if (matchId) return;
        if (queueStatus !== 'idle') {
            (async () => { await leaveQueue(); resetQueue(); })();
        }
    }, []);

    if (!user) return null;

    const winRate = formatWinRate(user.matches_won, user.matches_played);
    const isSearching = queueStatus !== 'idle';
    const recentMatches = (history || []).slice(0, 5);

    const stats = [
        { label: 'ELO Rating', value: formatElo(user.elo), icon: Trophy, color: 'from-amber-500 to-orange-600', glow: 'shadow-amber-500/20' },
        { label: 'Matches Played', value: user.matches_played, icon: Target, color: 'from-blue-500 to-cyan-500', glow: 'shadow-blue-500/20' },
        { label: 'Wins', value: user.matches_won, icon: Flame, color: 'from-emerald-500 to-green-500', glow: 'shadow-emerald-500/20' },
        { label: 'Win Rate', value: winRate, icon: TrendingUp, color: 'from-violet-500 to-purple-600', glow: 'shadow-violet-500/20' },
    ];

    return (
        <div className="min-h-screen bg-bg-root pb-20">
            {/* Subtle background glow */}
            <div className="absolute inset-x-0 top-0 h-[350px] pointer-events-none overflow-hidden">
                <div className="mx-auto w-[600px] h-[300px] bg-accent/5 rounded-full blur-3xl translate-y-[-30%]" />
            </div>

            {/* ── Main container ────────────────────────── */}
            <div className="dashboard-container relative z-10">

                {/* ── Welcome Header ─────────────────────── */}
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
                    <h1 className="text-3xl sm:text-4xl font-extrabold text-text-primary tracking-tight">
                        Welcome back,{' '}
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-accent-secondary">
                            {user.username}
                        </span>
                    </h1>
                    <p className="text-text-secondary mt-2 text-base">Your arena awaits. Let&apos;s climb the ranks.</p>
                </motion.div>

                {/* ── Stats Grid (4 cards) ───────────────── */}
                <div className="stats-grid">
                    {historyLoading
                        ? Array.from({ length: 4 }).map((_, i) => <div key={i}><StatCardSkeleton /></div>)
                        : stats.map((stat, i) => (
                            <motion.div
                                key={stat.label}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.4, delay: i * 0.1 }}
                            >
                                <div className={`stat-card relative overflow-hidden bg-bg-elevated/80 backdrop-blur-md border border-border transition-all duration-300 group hover:border-border-hover hover:shadow-xl ${stat.glow}`}>
                                    <div className={`absolute -top-6 -right-6 w-28 h-28 bg-gradient-to-br ${stat.color} opacity-[0.07] rounded-full group-hover:opacity-[0.12] transition-opacity duration-500`} />
                                    <div className={`relative z-10 w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-lg ${stat.glow} shrink-0`}>
                                        <stat.icon size={22} className="text-white" />
                                    </div>
                                    <div className="relative z-10 flex flex-col text-right">
                                        <p className="text-sm text-text-muted uppercase tracking-wider font-semibold mb-1">{stat.label}</p>
                                        <p className="text-2xl font-bold text-text-primary font-mono tracking-tight">{stat.value}</p>
                                    </div>
                                </div>
                            </motion.div>
                        ))
                    }
                </div>

                {/* ── Rating Graph + Find Match CTA ───────── */}
                <div className="graph-section">
                    <div>
                        {historyLoading ? <ChartSkeleton /> : <RatingChart history={history || []} currentElo={user.elo} />}
                    </div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="relative bg-bg-elevated/80 backdrop-blur-sm border border-border rounded-2xl p-8 flex flex-col items-center justify-center text-center overflow-hidden"
                    >
                        <div className="absolute inset-0 bg-gradient-to-br from-accent/[0.06] to-accent-secondary/[0.04]" />
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-40 h-40 bg-accent/10 rounded-full blur-3xl" />
                        <div className="relative z-10">
                            <motion.div
                                animate={{ y: [0, -8, 0] }}
                                transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
                                className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-accent to-accent-secondary flex items-center justify-center shadow-2xl mb-5"
                                style={{ boxShadow: '0 8px 40px rgba(124, 92, 252, 0.35)' }}
                            >
                                <Swords size={28} className="text-white" />
                            </motion.div>
                            <h3 className="text-xl font-bold text-text-primary mb-1.5">Ready for Battle?</h3>
                            <p className="text-sm text-text-secondary mb-6 max-w-[220px] mx-auto">
                                Queue up and duel an opponent near your rank
                            </p>
                            <Button variant="primary" size="lg" onClick={joinQueue} disabled={isSearching} loading={isSearching} className="w-full">
                                {isSearching ? 'Searching...' : '⚔ Find Match'}
                            </Button>
                        </div>
                    </motion.div>
                </div>

                {/* ── Recent Matches ─────────────────────── */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="recent-section bg-bg-elevated/80 backdrop-blur-sm border border-border rounded-2xl overflow-hidden"
                >
                    <div className="flex items-center justify-between px-6 py-5 border-b border-border/60">
                        <h3 className="text-xl font-semibold text-text-primary flex items-center gap-2.5">
                            <Clock size={20} className="text-accent" />
                            Recent Matches
                        </h3>
                        {recentMatches.length > 0 && (
                            <button
                                onClick={() => navigate('/history')}
                                className="flex items-center gap-1 text-sm text-accent hover:text-accent-hover font-medium transition-colors cursor-pointer"
                            >
                                View All <ChevronRight size={14} />
                            </button>
                        )}
                    </div>

                    {historyLoading ? (
                        <div className="divide-y divide-border/30">
                            {Array.from({ length: 3 }).map((_, i) => (
                                <div key={i} className="px-6 py-5 flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-full bg-bg-surface animate-pulse" />
                                        <div className="space-y-2">
                                            <div className="h-3.5 w-28 bg-bg-surface rounded animate-pulse" />
                                            <div className="h-2.5 w-20 bg-bg-surface rounded animate-pulse" />
                                        </div>
                                    </div>
                                    <div className="h-5 w-12 bg-bg-surface rounded animate-pulse" />
                                </div>
                            ))}
                        </div>
                    ) : isError ? (
                        <div className="py-16 text-center">
                            <p className="text-sm text-loss font-medium">Failed to load matches</p>
                            <p className="text-text-muted text-xs mt-1">Please try again later</p>
                        </div>
                    ) : recentMatches.length === 0 ? (
                        <div className="py-16 text-center">
                            <Swords size={40} className="mx-auto text-text-muted/40 mb-3" />
                            <p className="text-text-secondary text-sm font-medium">No matches yet</p>
                            <p className="text-text-muted text-xs mt-1">Start your first battle to see results here</p>
                        </div>
                    ) : (
                        <div className="divide-y divide-border/30">
                            {recentMatches.map((match, idx) => (
                                <RecentMatchRow key={match.id || idx} match={match} index={idx} />
                            ))}
                        </div>
                    )}
                </motion.div>
            </div>

            <QueueOverlay />
        </div>
    );
}

function RecentMatchRow({ match, index }) {
    const isWin = match.result === 'win';
    const isDraw = match.result === 'draw';
    const eloChange = (match.your_elo_after ?? match.your_elo_before) - match.your_elo_before;

    return (
        <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="flex items-center justify-between px-6 py-5 hover:bg-bg-hover/40 transition-colors group"
        >
            <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${isWin ? 'bg-win/15 text-win ring-1 ring-win/20'
                    : isDraw ? 'bg-draw/15 text-draw ring-1 ring-draw/20'
                        : 'bg-loss/15 text-loss ring-1 ring-loss/20'
                    }`}>
                    {isWin ? 'W' : isDraw ? 'D' : 'L'}
                </div>
                <div>
                    <p className="text-sm font-medium text-text-primary group-hover:text-accent transition-colors">
                        vs {match.opponent_username}
                    </p>
                    <p className="text-xs text-text-muted">
                        {match.started_at ? dayjs(match.started_at).fromNow() : '—'}
                        {match.opponent_elo && (
                            <span className="ml-1.5 text-text-muted/70">· {match.opponent_elo} ELO</span>
                        )}
                    </p>
                </div>
            </div>

            <div className="flex items-center gap-3">
                <Badge color={isWin ? 'green' : isDraw ? 'yellow' : 'red'}>
                    {isWin ? 'Win' : isDraw ? 'Draw' : 'Loss'}
                </Badge>
                <span className={`text-sm font-mono font-bold min-w-[44px] text-right ${eloChange > 0 ? 'text-win' : eloChange < 0 ? 'text-loss' : 'text-text-muted'
                    }`}>
                    {eloChange > 0 ? `+${eloChange}` : eloChange}
                </span>
            </div>
        </motion.div>
    );
}
