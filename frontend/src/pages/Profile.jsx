import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
    Swords, Users, Clock, TrendingUp, TrendingDown, Minus, Zap, Sparkles,
} from 'lucide-react';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import { useAuthStore } from '../stores/authStore';
import { useMatchmakingStore } from '../stores/matchmakingStore';
import { matchApi } from '../api/auth';
import { formatWinRate, formatElo } from '../utils/formatters';
import RatingChart from '../components/dashboard/RatingChart';
import QueueOverlay from '../components/matchmaking/QueueOverlay';
import PrivateRoomOverlay from '../components/matchmaking/PrivateRoomOverlay';
import { StatCardSkeleton, ChartSkeleton } from '../components/ui/Skeleton';

dayjs.extend(relativeTime);

const Fade = ({ children, delay = 0, className = '' }) => (
    <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay, ease: [0.22, 1, 0.36, 1] }}
        className={className}
    >
        {children}
    </motion.div>
);

export default function Profile() {
    const user = useAuthStore((s) => s.user);
    const queueStatus = useMatchmakingStore((s) => s.status);
    const joinQueue = useMatchmakingStore((s) => s.joinQueue);
    const navigate = useNavigate();
    const [privateOverlayOpen, setPrivateOverlayOpen] = useState(false);

    const { data: history = [], isLoading } = useQuery({
        queryKey: ['matchHistory'],
        queryFn: matchApi.getHistory,
        enabled: !!user,
    });

    const { winCount, lossCount, drawCount, peakElo, avgDuration } = useMemo(() => {
        let w = 0, l = 0, d = 0, peak = 0, totalDur = 0, durCount = 0;
        history.forEach((m) => {
            if (m.result === 'win') w++;
            else if (m.result === 'loss') l++;
            else d++;
            const elo = m.your_elo_after ?? m.your_elo_before;
            if (elo > peak) peak = elo;
            if (m.duration_seconds) {
                totalDur += m.duration_seconds;
                durCount++;
            }
        });
        const avg = durCount > 0 ? Math.round(totalDur / durCount) : 0;
        const avgMin = Math.floor(avg / 60);
        const avgSec = avg % 60;
        return {
            winCount: w,
            lossCount: l,
            drawCount: d,
            peakElo: peak || user?.elo || 0,
            avgDuration: avg > 0 ? `${String(avgMin).padStart(2, '0')}:${String(avgSec).padStart(2, '0')}` : '--:--',
        };
    }, [history, user]);

    if (!user) return null;

    const winRate = formatWinRate(user.matches_won, user.matches_played);
    const isSearching = queueStatus !== 'idle';
    const recentMatches = [...history]
        .sort((a, b) => new Date(b.started_at) - new Date(a.started_at))
        .slice(0, 6);

    const stats = [
        { label: 'ELO_RATING', value: formatElo(user.elo), sub: user.matches_played < 10 ? 'PROVISIONAL' : null },
        { label: 'TOTAL_MATCHES', value: user.matches_played },
        { label: 'WINS_CONFIRMED', value: user.matches_won },
        { label: 'WIN_RATE', value: winRate, highlight: true },
    ];

    return (
        <div className="min-h-screen bg-bg-root">
            <div className="max-w-[1360px] mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-20">

                {/* ═══ MAIN TWO-COLUMN LAYOUT ═══ */}
                <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6 items-start">

                    {/* ── LEFT COLUMN: all main content ── */}
                    <div className="flex flex-col gap-6 min-w-0">

                        {/* Profile Header */}
                        <Fade>
                            <div className="paper-card grain-panel p-6 sm:p-8">
                                <div className="flex items-start gap-4 mb-1">
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs font-mono font-bold uppercase tracking-[0.14em] text-text-muted">
                                            OPERATOR_ACTIVE
                                        </span>
                                        <span className="w-2 h-2 rounded-full bg-win animate-pulse" />
                                    </div>
                                </div>
                                <h1 className="text-3xl sm:text-4xl font-black text-text-primary tracking-[-0.04em] uppercase mt-2">
                                    {user.username}
                                </h1>
                                <p className="text-sm font-mono text-text-muted mt-2 tracking-wide">
                                    {user.email}
                                </p>

                                {/* Inline stat badges */}
                                <div className="flex flex-wrap gap-4 mt-6">
                                    <div className="border border-border bg-bg-secondary/50 px-5 py-3 min-w-[130px]">
                                        <p className="text-[10px] font-mono font-bold uppercase tracking-[0.12em] text-text-muted">
                                            PEAK_ELO
                                        </p>
                                        <p className="text-xl font-black text-accent mt-1">{formatElo(peakElo)}</p>
                                    </div>
                                    <div className="border border-border bg-bg-secondary/50 px-5 py-3 min-w-[130px]">
                                        <p className="text-[10px] font-mono font-bold uppercase tracking-[0.12em] text-text-muted">
                                            MATCHES_PLAYED
                                        </p>
                                        <p className="text-xl font-black text-text-primary mt-1">{user.matches_played}</p>
                                    </div>
                                </div>
                            </div>
                        </Fade>

                        {/* Stats Row */}
                        <Fade delay={0.1}>
                            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                                {isLoading
                                    ? Array.from({ length: 4 }).map((_, i) => (
                                        <div key={i} className="paper-card p-5"><StatCardSkeleton /></div>
                                    ))
                                    : stats.map((s, i) => (
                                        <motion.div
                                            key={s.label}
                                            initial={{ opacity: 0, y: 14 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.12 + i * 0.05 }}
                                            className={`paper-card grain-panel p-5 ${s.highlight ? 'border-t-2 border-t-accent' : ''}`}
                                        >
                                            <p className="text-[10px] font-mono font-bold uppercase tracking-[0.12em] text-text-muted">
                                                {s.label}
                                            </p>
                                            <div className="flex items-end gap-2 mt-2">
                                                <span className={`text-2xl sm:text-3xl font-black leading-none ${s.highlight ? 'text-accent' : 'text-text-primary'}`}>
                                                    {s.value}
                                                </span>
                                                {s.sub && (
                                                    <span className="text-[10px] font-mono font-bold text-text-muted uppercase tracking-wider pb-0.5">
                                                        {s.sub}
                                                    </span>
                                                )}
                                                {s.highlight && <TrendingUp size={16} className="text-accent mb-1" />}
                                            </div>
                                        </motion.div>
                                    ))
                                }
                            </div>
                        </Fade>

                        {/* Chart + Match Analytics */}
                        <div className="grid grid-cols-1 xl:grid-cols-[1.4fr_1fr] gap-6">
                            <Fade delay={0.18}>
                                <div className="h-[420px]">
                                    {isLoading ? <ChartSkeleton /> : <RatingChart history={history} currentElo={user.elo} />}
                                </div>
                            </Fade>

                            <Fade delay={0.22}>
                                <div className="paper-card grain-panel p-6 flex flex-col">
                                    <h3 className="text-xs font-mono font-bold uppercase tracking-[0.14em] text-text-primary mb-6">
                                        MATCH_ANALYTICS
                                    </h3>

                                    {history.length === 0 ? (
                                        <p className="text-sm text-text-muted text-center py-10">
                                            No match data yet. Play some matches!
                                        </p>
                                    ) : (
                                        <>
                                            <div className="space-y-5 flex-1">
                                                {[
                                                    { label: 'WINS', count: winCount, total: history.length, color: 'bg-win' },
                                                    { label: 'LOSSES', count: lossCount, total: history.length, color: 'bg-loss' },
                                                ].map(({ label, count, total, color }) => {
                                                    const pct = total > 0 ? Math.round((count / total) * 100) : 0;
                                                    return (
                                                        <div key={label}>
                                                            <div className="flex items-center justify-between mb-2">
                                                                <span className="text-xs font-mono font-bold uppercase tracking-[0.1em] text-text-secondary">
                                                                    {label}
                                                                </span>
                                                                <span className="text-sm font-bold text-text-primary font-mono">
                                                                    {count} / {total}
                                                                </span>
                                                            </div>
                                                            <div className="w-full h-3 bg-bg-surface rounded-sm overflow-hidden">
                                                                <motion.div
                                                                    initial={{ width: 0 }}
                                                                    animate={{ width: `${pct}%` }}
                                                                    transition={{ duration: 0.8, delay: 0.2 }}
                                                                    className={`h-full ${color}`}
                                                                />
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                            </div>

                                            <div className="grid grid-cols-2 gap-4 mt-6 pt-5 border-t border-border">
                                                <div className="border border-border bg-bg-secondary/50 px-4 py-3 text-center">
                                                    <p className="text-[10px] font-mono font-bold uppercase tracking-[0.12em] text-text-muted">
                                                        AVG_TIME
                                                    </p>
                                                    <p className="text-xl font-black text-text-primary mt-1 font-mono">
                                                        {avgDuration}
                                                    </p>
                                                </div>
                                                <div className="border border-border bg-bg-secondary/50 px-4 py-3 text-center">
                                                    <p className="text-[10px] font-mono font-bold uppercase tracking-[0.12em] text-text-muted">
                                                        PEAK_ELO
                                                    </p>
                                                    <p className="text-xl font-black text-text-primary mt-1 font-mono">
                                                        {peakElo}
                                                    </p>
                                                </div>
                                            </div>
                                        </>
                                    )}
                                </div>
                            </Fade>
                        </div>

                        {/* Chronological Log */}
                        <Fade delay={0.28}>
                            <div className="paper-card grain-panel overflow-hidden">
                                <div className="flex items-center justify-between px-6 py-5 border-b border-border">
                                    <h3 className="text-xs font-mono font-bold uppercase tracking-[0.14em] text-text-primary">
                                        CHRONOLOGICAL_LOG
                                    </h3>
                                    <button
                                        onClick={() => navigate('/history')}
                                        className="text-xs font-mono font-bold uppercase tracking-[0.1em] text-accent hover:text-accent-hover transition-colors cursor-pointer"
                                    >
                                        VIEW_ALL_ARCHIVES
                                    </button>
                                </div>

                                {isLoading ? (
                                    <div className="p-6 space-y-4">
                                        {Array.from({ length: 3 }).map((_, i) => (
                                            <div key={i} className="flex items-center gap-4">
                                                <div className="h-8 w-16 bg-bg-surface rounded animate-pulse" />
                                                <div className="h-4 w-32 bg-bg-surface rounded animate-pulse" />
                                                <div className="h-4 w-20 bg-bg-surface rounded animate-pulse flex-1" />
                                            </div>
                                        ))}
                                    </div>
                                ) : recentMatches.length === 0 ? (
                                    <div className="py-14 text-center">
                                        <Swords size={28} className="mx-auto text-text-muted/30 mb-3" />
                                        <p className="text-sm text-text-secondary">No matches yet</p>
                                        <p className="text-xs text-text-muted mt-1">Start a battle to populate the log</p>
                                    </div>
                                ) : (
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-sm">
                                            <thead className="text-[10px] font-mono font-bold uppercase tracking-[0.12em] text-text-muted border-b border-border/50">
                                                <tr>
                                                    <th className="text-left px-6 py-3">STATUS</th>
                                                    <th className="text-left px-6 py-3">OPPONENT</th>
                                                    <th className="text-left px-6 py-3">OUTCOME_FLUX</th>
                                                    <th className="text-left px-6 py-3 hidden md:table-cell">DURATION</th>
                                                    <th className="text-left px-6 py-3 hidden sm:table-cell">TIMESTAMP</th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-border/30">
                                                {recentMatches.map((match, idx) => {
                                                    const eloChange = (match.your_elo_after ?? match.your_elo_before) - match.your_elo_before;
                                                    const isWin = match.result === 'win';
                                                    const isDraw = match.result === 'draw';
                                                    const dur = match.duration_seconds
                                                        ? match.duration_seconds >= 60
                                                            ? `${String(Math.floor(match.duration_seconds / 60)).padStart(2, '0')}m ${String(match.duration_seconds % 60).padStart(2, '0')}s`
                                                            : `${match.duration_seconds}s`
                                                        : '—';

                                                    return (
                                                        <motion.tr
                                                            key={match.id || idx}
                                                            initial={{ opacity: 0, x: -8 }}
                                                            animate={{ opacity: 1, x: 0 }}
                                                            transition={{ delay: idx * 0.04 }}
                                                            className="hover:bg-bg-hover/40 transition-colors"
                                                        >
                                                            <td className="px-6 py-4">
                                                                <span className={`inline-flex items-center justify-center min-w-[60px] px-2.5 py-1 text-[10px] font-mono font-bold uppercase tracking-wider border ${
                                                                    isWin
                                                                        ? 'bg-win/10 text-win border-win/25'
                                                                        : isDraw
                                                                            ? 'bg-draw/10 text-draw border-draw/25'
                                                                            : 'bg-loss/10 text-loss border-loss/25'
                                                                }`}>
                                                                    {isWin ? 'WIN' : isDraw ? 'DRAW' : 'LOSS'}
                                                                </span>
                                                            </td>
                                                            <td className="px-6 py-4">
                                                                <span className="font-bold text-text-primary tracking-wide">
                                                                    {(match.opponent_username || 'unknown').toLowerCase().replace(/\s+/g, '_')}
                                                                </span>
                                                            </td>
                                                            <td className="px-6 py-4">
                                                                <span className={`font-mono font-bold ${
                                                                    eloChange > 0 ? 'text-win' : eloChange < 0 ? 'text-loss' : 'text-text-muted'
                                                                }`}>
                                                                    {eloChange > 0 ? '+' : ''}{eloChange} ELO
                                                                </span>
                                                            </td>
                                                            <td className="px-6 py-4 hidden md:table-cell">
                                                                <span className="text-text-secondary font-mono text-xs">
                                                                    {dur}
                                                                </span>
                                                            </td>
                                                            <td className="px-6 py-4 hidden sm:table-cell">
                                                                <span className="text-text-muted font-mono text-xs">
                                                                    {match.started_at ? dayjs(match.started_at).format('YYYY-MM-DD HH:mm') : '—'}
                                                                </span>
                                                            </td>
                                                        </motion.tr>
                                                    );
                                                })}
                                            </tbody>
                                        </table>
                                    </div>
                                )}

                                {recentMatches.length > 0 && (
                                    <div className="border-t border-border/50 py-4 text-center">
                                        <button
                                            onClick={() => navigate('/history')}
                                            className="text-xs font-mono font-bold uppercase tracking-[0.12em] text-text-muted hover:text-accent transition-colors cursor-pointer"
                                        >
                                            LOAD_MORE_ARCHIVES
                                        </button>
                                    </div>
                                )}
                            </div>
                        </Fade>
                    </div>

                    {/* ── RIGHT SIDEBAR: sticky alongside all content ── */}
                    <div className="flex flex-col gap-5 lg:sticky lg:top-[84px]">
                        <Fade delay={0.08}>
                            <div className="paper-card grain-panel p-6 border-t-3 border-t-accent">
                                <h3 className="text-base font-black text-text-primary uppercase tracking-[-0.01em]">
                                    INITIALIZE_MATCH
                                </h3>
                                <p className="text-sm text-text-secondary mt-2 leading-relaxed">
                                    Jump into a ranked battle or play with a friend.
                                </p>
                                <button
                                    onClick={joinQueue}
                                    disabled={isSearching}
                                    className="w-full mt-4 flex items-center justify-center gap-2 bg-accent hover:bg-accent-hover text-white px-4 py-3.5 font-mono text-sm font-bold uppercase tracking-[0.08em] transition-all cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
                                >
                                    {isSearching ? (
                                        <span className="animate-pulse flex items-center gap-2">
                                            <Zap size={16} /> SEARCHING...
                                        </span>
                                    ) : (
                                        <><Swords size={16} /> QUICK_DEPLOYMENT</>
                                    )}
                                </button>
                                <button
                                    onClick={() => setPrivateOverlayOpen(true)}
                                    className="w-full mt-2 flex items-center justify-center gap-2 border border-border bg-bg-secondary hover:bg-bg-hover text-text-primary px-4 py-3.5 font-mono text-sm font-bold uppercase tracking-[0.08em] transition-all cursor-pointer"
                                >
                                    <Users size={16} /> PLAY_WITH_FRIEND
                                </button>
                            </div>
                        </Fade>

                        <Fade delay={0.16}>
                            <div className="paper-card grain-panel p-5">
                                <h4 className="text-xs font-mono font-bold uppercase tracking-[0.12em] text-text-muted mb-4">
                                    QUICK_LINKS
                                </h4>
                                <div className="flex flex-col gap-2">
                                    <button
                                        onClick={() => navigate('/problems')}
                                        className="text-left text-sm font-semibold text-text-secondary hover:text-accent transition-colors px-2 py-1.5 cursor-pointer"
                                    >
                                        → Practice Problems
                                    </button>
                                    <button
                                        onClick={() => navigate('/history')}
                                        className="text-left text-sm font-semibold text-text-secondary hover:text-accent transition-colors px-2 py-1.5 cursor-pointer"
                                    >
                                        → Full Match History
                                    </button>
                                    <button
                                        onClick={() => navigate('/settings')}
                                        className="text-left text-sm font-semibold text-text-secondary hover:text-accent transition-colors px-2 py-1.5 cursor-pointer"
                                    >
                                        → Settings
                                    </button>
                                </div>
                            </div>
                        </Fade>
                    </div>
                </div>

                {/* ═══ FOOTER ═══ */}
                <div className="flex items-center justify-between pt-6 mt-8 border-t border-border text-xs">
                    <span className="text-accent font-bold tracking-wide uppercase">CodeArena</span>
                    <span className="text-text-muted">
                        © {new Date().getFullYear()} CodeArena. All rights reserved.
                    </span>
                </div>
            </div>

            <QueueOverlay />
            <PrivateRoomOverlay isOpen={privateOverlayOpen} onClose={() => setPrivateOverlayOpen(false)} />
        </div>
    );
}
