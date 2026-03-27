import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
    Trophy, Target, Flame, TrendingUp, Swords, Clock, ChevronRight, Users,
} from 'lucide-react';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import { useAuthStore } from '../stores/authStore';
import { useBattleStore } from '../stores/battleStore';
import { useMatchmakingStore } from '../stores/matchmakingStore';
import { matchApi } from '../api/auth';
import { formatWinRate, formatElo } from '../utils/formatters';
import QueueOverlay from '../components/matchmaking/QueueOverlay';
import PrivateRoomOverlay from '../components/matchmaking/PrivateRoomOverlay';
import RatingChart from '../components/dashboard/RatingChart';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { StatCardSkeleton, ChartSkeleton } from '../components/ui/Skeleton';

dayjs.extend(relativeTime);

export default function Dashboard() {
    const user = useAuthStore((s) => s.user);
    const queueStatus = useMatchmakingStore((s) => s.status);
    const joinQueue = useMatchmakingStore((s) => s.joinQueue);
    const hasInitializedRef = useRef(false);
    const navigate = useNavigate();
    const [privateOverlayOpen, setPrivateOverlayOpen] = useState(false);

    const { data: history, isLoading: historyLoading, isError } = useQuery({
        queryKey: ['matchHistory'],
        queryFn: matchApi.getHistory,
        enabled: !!user,
    });

    useEffect(() => {
        if (hasInitializedRef.current) return;
        hasInitializedRef.current = true;
    }, []);

    if (!user) return null;

    const winRate = formatWinRate(user.matches_won, user.matches_played);
    const isSearching = queueStatus !== 'idle';
    const recentMatches = (history || []).slice(0, 5);

    const stats = [
        { label: 'ELO Rating', value: formatElo(user.elo), icon: Trophy },
        { label: 'Matches Played', value: user.matches_played, icon: Target },
        { label: 'Wins', value: user.matches_won, icon: Flame },
        { label: 'Win Rate', value: winRate, icon: TrendingUp },
    ];

    return (
        <div className="min-h-screen bg-bg-root pb-20">

            <div className="dashboard-container relative z-10">
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
                    <h1 className="text-3xl sm:text-4xl font-extrabold text-text-primary tracking-tight">
                        Welcome back,{' '}
                        <span className="text-accent">{user.username}</span>
                    </h1>
                    <p className="text-text-secondary mt-2 text-base">Your arena awaits. Let&apos;s climb the ranks.</p>
                </motion.div>

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
                                <div className="stat-card bg-bg-secondary border border-border transition-colors duration-200 hover:border-border-hover">
                                    <div className="w-11 h-11 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
                                        <stat.icon size={20} className="text-accent" />
                                    </div>
                                    <div className="flex flex-col text-right">
                                        <p className="text-xs text-text-muted uppercase tracking-wider font-semibold mb-1">{stat.label}</p>
                                        <p className="text-2xl font-bold text-text-primary font-mono tracking-tight">{stat.value}</p>
                                    </div>
                                </div>
                            </motion.div>
                        ))
                    }
                </div>

                <div className="graph-section">
                    <div>
                        {historyLoading ? <ChartSkeleton /> : <RatingChart history={history || []} currentElo={user.elo} />}
                    </div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="bg-bg-secondary border border-border rounded-xl flex flex-col overflow-hidden"
                    >
                        <div className="flex-1 flex flex-col items-center justify-center text-center p-8 pb-10">
                            <div className="w-14 h-14 mx-auto rounded-xl bg-accent flex items-center justify-center mb-5">
                                <Swords size={26} className="text-white" />
                            </div>
                            <h3 className="text-xl font-bold text-text-primary mb-1.5">Ready for Battle?</h3>
                            <p className="text-sm text-text-secondary max-w-60 mx-auto">
                                Queue up and duel an opponent near your rank
                            </p>
                        </div>

                        <div className="w-full mt-auto flex flex-col gap-2 px-6 pb-6 pt-2">
                            <button
                                onClick={joinQueue}
                                disabled={isSearching}
                                className="w-full py-4 px-6 bg-accent hover:bg-accent-hover text-white font-bold text-lg transition-colors disabled:opacity-75 disabled:cursor-not-allowed flex items-center justify-center gap-2 rounded-xl shadow-lg shadow-accent/20"
                            >
                                {isSearching ? (
                                    <span className="animate-pulse flex items-center gap-2">
                                        Searching...
                                    </span>
                                ) : (
                                    <>
                                        <Swords size={20} />
                                        Find Match
                                    </>
                                )}
                            </button>
                            <button
                                onClick={() => setPrivateOverlayOpen(true)}
                                className="w-full py-3.5 px-6 bg-bg-surface hover:bg-bg-hover border border-border text-text-primary font-semibold text-base transition-colors flex items-center justify-center gap-2 rounded-xl"
                            >
                                <Users size={18} className="text-accent" />
                                Play with Friend
                            </button>
                        </div>
                    </motion.div>
                </div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="recent-section bg-bg-secondary border border-border rounded-xl overflow-hidden"
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
            <PrivateRoomOverlay isOpen={privateOverlayOpen} onClose={() => setPrivateOverlayOpen(false)} />
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
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${isWin ? 'bg-win/15 text-win'
                    : isDraw ? 'bg-draw/15 text-draw'
                        : 'bg-loss/15 text-loss'
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
                <span className={`text-sm font-mono font-bold min-w-11 text-right ${eloChange > 0 ? 'text-win' : eloChange < 0 ? 'text-loss' : 'text-text-muted'
                    }`}>
                    {eloChange > 0 ? `+${eloChange}` : eloChange}
                </span>
            </div>
        </motion.div>
    );
}