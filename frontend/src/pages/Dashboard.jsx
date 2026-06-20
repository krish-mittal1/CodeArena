import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
    Swords, Users, ChevronRight, Clock, BookOpen, Trophy,
    Zap, ArrowRight,
} from 'lucide-react';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import { useAuthStore } from '../stores/authStore';
import { useMatchmakingStore } from '../stores/matchmakingStore';
import { matchApi } from '../api/auth';
import { formatWinRate, formatElo } from '../utils/formatters';
import QueueOverlay from '../components/matchmaking/QueueOverlay';
import PrivateRoomOverlay from '../components/matchmaking/PrivateRoomOverlay';
import RatingChart from '../components/dashboard/RatingChart';
import { StatCardSkeleton, ChartSkeleton } from '../components/ui/Skeleton';

dayjs.extend(relativeTime);

/* ── Animate-in ───────────────────────────── */
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

export default function Dashboard() {
    const user = useAuthStore((s) => s.user);
    const queueStatus = useMatchmakingStore((s) => s.status);
    const joinQueue = useMatchmakingStore((s) => s.joinQueue);
    const navigate = useNavigate();
    const [privateOverlayOpen, setPrivateOverlayOpen] = useState(false);
    const [fakeOnline] = useState(() => Math.floor(Math.random() * 400) + 800);
    const [fakeWait] = useState(() => Math.floor(Math.random() * 50) + 15);

    const { data: history, isLoading, isError } = useQuery({
        queryKey: ['matchHistory'],
        queryFn: matchApi.getHistory,
        enabled: !!user,
    });

    if (!user) return null;

    const winRate = formatWinRate(user.matches_won, user.matches_played);
    const isSearching = queueStatus !== 'idle';
    const allMatches = history || [];
    const recentMatches = allMatches.slice(0, 5);

    const stats = [
        { label: 'ELO RATING', value: formatElo(user.elo) },
        { label: 'MATCHES PLAYED', value: user.matches_played },
        { label: 'WINS', value: user.matches_won },
        { label: 'WIN RATE', value: winRate },
    ];

    return (
        <div className="min-h-screen bg-bg-root">
            <div className="db-wrap">

                {/* ═══ HERO HEADLINE ═══ */}
                <Fade>
                    <div className="db-hero">
                        <h1 className="db-hero__title">
                            <span className="text-text-primary">{user.username},</span>{' '}
                            <span className="text-accent">YOUR NEXT MATCH IS WAITING.</span>
                        </h1>
                        <p className="db-hero__sub">
                            Queue up, check the tape, and keep the rating moving. The foundry awaits your next commit.
                        </p>
                    </div>
                </Fade>

                {/* ═══ MAIN GRID: Left content + Right sidebar ═══ */}
                <div className="db-grid">

                    {/* ── LEFT COLUMN ────────────────────────── */}
                    <div className="db-left">

                        {/* Stats Row */}
                        <Fade delay={0.06}>
                            <div className="db-stats">
                                {isLoading
                                    ? Array.from({ length: 4 }).map((_, i) => (
                                        <div key={i} className="db-stat"><StatCardSkeleton /></div>
                                    ))
                                    : stats.map((s, i) => (
                                        <motion.div
                                            key={s.label}
                                            initial={{ opacity: 0, y: 14 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.08 + i * 0.06 }}
                                            className="db-stat"
                                        >
                                            <span className="db-stat__label">{s.label}</span>
                                            <span className="db-stat__value">{s.value}</span>
                                        </motion.div>
                                    ))
                                }
                            </div>
                        </Fade>

                        {/* Rating Chart */}
                        <Fade delay={0.14}>
                            {isLoading ? <ChartSkeleton /> : <RatingChart history={allMatches} currentElo={user.elo} />}
                        </Fade>

                        {/* Recent Operations */}
                        <Fade delay={0.2}>
                            <div className="db-recent paper-card grain-panel">
                                <div className="db-recent__header">
                                    <h3 className="db-section-title">RECENT OPERATIONS</h3>
                                    <span className="db-recent__count">LATEST {recentMatches.length} ENTRIES</span>
                                </div>

                                {isLoading ? (
                                    <div className="db-recent__loading">
                                        {Array.from({ length: 3 }).map((_, i) => (
                                            <div key={i} className="db-recent__skel">
                                                <div className="h-9 w-9 rounded-lg bg-bg-surface animate-pulse" />
                                                <div className="flex-1 space-y-2">
                                                    <div className="h-3.5 w-36 bg-bg-surface rounded animate-pulse" />
                                                    <div className="h-2.5 w-20 bg-bg-surface rounded animate-pulse" />
                                                </div>
                                                <div className="h-4 w-16 bg-bg-surface rounded animate-pulse" />
                                            </div>
                                        ))}
                                    </div>
                                ) : isError ? (
                                    <div className="py-14 text-center">
                                        <p className="text-sm text-loss font-medium">Failed to load matches</p>
                                    </div>
                                ) : recentMatches.length === 0 ? (
                                    <div className="py-14 text-center">
                                        <Swords size={32} className="mx-auto text-text-muted/30 mb-3" />
                                        <p className="text-text-secondary text-sm font-medium">No matches yet</p>
                                        <p className="text-text-muted text-xs mt-1">Deploy your first battle to populate the log</p>
                                    </div>
                                ) : (
                                    <div className="db-recent__list">
                                        {recentMatches.map((match, idx) => (
                                            <RecentRow key={match.id || idx} match={match} index={idx} />
                                        ))}
                                    </div>
                                )}
                            </div>
                        </Fade>
                    </div>

                    {/* ── RIGHT SIDEBAR ──────────────────────── */}
                    <div className="db-sidebar">

                        {/* Battle Card */}
                        <Fade delay={0.1}>
                            <div className="db-battle paper-card grain-panel">
                                <h3 className="db-battle__title">READY FOR BATTLE?</h3>
                                <p className="db-battle__sub">
                                    System status: <strong className="text-text-primary">OPTIMAL</strong>. Multiple skirmishes
                                    currently active in your skill bracket.
                                </p>

                                <button
                                    onClick={joinQueue}
                                    disabled={isSearching}
                                    className="db-battle__btn db-battle__btn--primary"
                                    id="dashboard-find-match"
                                >
                                    {isSearching ? (
                                        <span className="animate-pulse flex items-center gap-2 justify-center">
                                            <Zap size={16} /> SEARCHING...
                                        </span>
                                    ) : (
                                        <>
                                            <Swords size={16} />
                                            FIND MATCH
                                        </>
                                    )}
                                </button>

                                <button
                                    onClick={() => setPrivateOverlayOpen(true)}
                                    className="db-battle__btn db-battle__btn--secondary"
                                    id="dashboard-play-friend"
                                >
                                    <Users size={16} />
                                    PLAY WITH FRIEND
                                </button>

                                <div className="db-battle__meta">
                                    <div className="db-battle__meta-row">
                                        <span>ACTIVE CODESMITHS</span>
                                        <span className="db-battle__meta-val">{fakeOnline.toLocaleString()}</span>
                                    </div>
                                    <div className="db-battle__meta-row">
                                        <span>EST. WAIT TIME</span>
                                        <span className="db-battle__meta-val">00:{String(fakeWait).padStart(2, '0')}s</span>
                                    </div>
                                </div>
                            </div>
                        </Fade>

                        {/* Practice Card */}
                        <Fade delay={0.18}>
                            <button
                                onClick={() => navigate('/problems')}
                                className="db-sidebar-card paper-card grain-panel group"
                            >
                                <div className="db-sidebar-card__icon">
                                    <BookOpen size={20} />
                                </div>
                                <ArrowRight size={18} className="db-sidebar-card__arrow" />
                                <h4 className="db-sidebar-card__title">PRACTICE</h4>
                                <p className="db-sidebar-card__desc">Sharpen your skills with curated problems.</p>
                            </button>
                        </Fade>

                        {/* History Card */}
                        <Fade delay={0.24}>
                            <button
                                onClick={() => navigate('/history')}
                                className="db-sidebar-card paper-card grain-panel group"
                            >
                                <div className="db-sidebar-card__icon">
                                    <Trophy size={20} />
                                </div>
                                <ArrowRight size={18} className="db-sidebar-card__arrow" />
                                <h4 className="db-sidebar-card__title">MATCH HISTORY</h4>
                                <p className="db-sidebar-card__desc">Review past operations and ELO flux.</p>
                            </button>
                        </Fade>
                    </div>
                </div>

                {/* ═══ FOOTER ═══ */}
                <div className="db-footer">
                    <span className="text-accent font-bold tracking-wide">CODEARENA</span>
                    <span className="text-text-muted text-xs">
                        © {new Date().getFullYear()} CodeArena Terminal Foundry. All rights reserved.
                    </span>
                </div>
            </div>

            <QueueOverlay />
            <PrivateRoomOverlay isOpen={privateOverlayOpen} onClose={() => setPrivateOverlayOpen(false)} />
        </div>
    );
}

/* ── Recent Match Row ─────────────────────── */
function RecentRow({ match, index }) {
    const isWin = match.result === 'win';
    const isDraw = match.result === 'draw';
    const eloChange = (match.your_elo_after ?? match.your_elo_before) - match.your_elo_before;

    const opName = match.opponent_username || 'unknown';
    const timeAgo = match.started_at ? dayjs(match.started_at).fromNow() : '';

    return (
        <motion.div
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.04 }}
            className="db-recent__row"
        >
            <div className={`db-recent__icon ${isWin ? 'db-recent__icon--win' : isDraw ? 'db-recent__icon--draw' : 'db-recent__icon--loss'}`}>
                {isWin ? <Swords size={16} /> : isDraw ? <Clock size={16} /> : <Swords size={16} />}
            </div>

            <div className="db-recent__info">
                <span className="db-recent__name">
                    {opName.toUpperCase().replace(/\s+/g, '_')}
                </span>
                <span className="db-recent__time">{timeAgo.toUpperCase()}</span>
            </div>

            <div className="db-recent__result">
                <span className={`db-recent__elo ${eloChange > 0 ? 'text-win' : eloChange < 0 ? 'text-loss' : 'text-text-muted'}`}>
                    {eloChange > 0 ? '+' : ''}{eloChange} ELO
                </span>
                <span className={`db-recent__badge ${isWin ? 'db-recent__badge--win' : isDraw ? 'db-recent__badge--draw' : 'db-recent__badge--loss'}`}>
                    {isWin ? 'WIN' : isDraw ? 'DRAW' : 'LOSS'}
                </span>
            </div>
        </motion.div>
    );
}
