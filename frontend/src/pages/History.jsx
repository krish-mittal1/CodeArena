import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import {
    History as HistoryIcon, Filter, ChevronLeft, ChevronRight, Swords,
    Calendar, Trophy, Clock, TrendingUp, TrendingDown, User, Minus
} from 'lucide-react';
import dayjs from 'dayjs';
import { useAuthStore } from '../stores/authStore';
import { matchApi } from '../api/auth';
import Modal from '../components/ui/Modal';
import EmptyState from '../components/ui/EmptyState';
import { TableRowSkeleton } from '../components/ui/Skeleton';

const ITEMS_PER_PAGE = 15;

export default function HistoryPage() {
    const user = useAuthStore((s) => s.user);
    const [filterResult, setFilterResult] = useState('all');
    const [page, setPage] = useState(1);
    const [selectedMatch, setSelectedMatch] = useState(null);

    const { data: history = [], isLoading, isError } = useQuery({
        queryKey: ['matchHistory'],
        queryFn: matchApi.getHistory,
        enabled: !!user,
    });

    const filtered = useMemo(() => {
        let items = [...history];
        if (filterResult !== 'all') {
            items = items.filter((m) => m.result === filterResult);
        }
        items.sort((a, b) => new Date(b.started_at) - new Date(a.started_at));
        return items;
    }, [history, filterResult]);

    const totalPages = Math.ceil(filtered.length / ITEMS_PER_PAGE);
    const paginated = filtered.slice((page - 1) * ITEMS_PER_PAGE, page * ITEMS_PER_PAGE);

    return (
        <div className="min-h-[calc(100vh-64px)] w-full bg-bg-root flex flex-col">
            <div className="w-full max-w-[1600px] mx-auto px-6 sm:px-10 py-10 pb-12 flex-1">

                {/* Header & Filters */}
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8"
                >
                    <div className="flex items-center gap-6">
                        <div className="w-14 h-14 bg-accent/10 rounded-2xl flex items-center justify-center border border-accent/30 shadow-inner">
                            <HistoryIcon size={28} className="text-accent" />
                        </div>
                        <div className="pt-1">
                            <h1 className="text-2xl sm:text-3xl font-bold text-text-primary tracking-wide">
                                Match History
                            </h1>
                            <p className="text-text-secondary text-sm font-medium mt-1">
                                {filtered.length} total matches played
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-1 p-1.5 bg-bg-secondary border border-border rounded-xl backdrop-blur-sm shadow-inner">
                        {['all', 'win', 'loss', 'draw'].map((val) => (
                            <button
                                key={val}
                                onClick={() => { setFilterResult(val); setPage(1); }}
                                className={`px-5 py-2 text-sm font-semibold capitalize rounded-lg transition-all ${filterResult === val
                                    ? 'bg-accent text-white shadow-md'
                                    : 'bg-transparent text-text-secondary hover:text-text-primary hover:bg-bg-hover'
                                    }`}
                            >
                                {val}
                            </button>
                        ))}
                    </div>
                </motion.div>

                {/* Table Card */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-bg-elevated/80 backdrop-blur-xl border border-border rounded-3xl shadow-2xl overflow-hidden"
                >
                    {isLoading ? (
                        <table className="w-full text-sm">
                            <tbody>
                                {Array.from({ length: 5 }).map((_, i) => (
                                    <TableRowSkeleton key={i} cols={6} />
                                ))}
                            </tbody>
                        </table>
                    ) : isError ? (
                        <div className="py-24 text-center">
                            <p className="text-loss text-sm font-medium">Failed to load match history.</p>
                        </div>
                    ) : filtered.length === 0 ? (
                        <div className="py-16">
                            <EmptyState
                                icon={Swords}
                                title="No matches found"
                                description="Play some matches to see your history appear here."
                            />
                        </div>
                    ) : (
                        <>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm text-left border-collapse">
                                    <thead className="text-xs uppercase tracking-widest text-text-muted bg-bg-secondary/40 border-b border-border">
                                        <tr>
                                            <th className="px-6 py-5 font-bold">Opponent</th>
                                            <th className="px-6 py-5 font-bold">Result</th>
                                            <th className="px-6 py-5 font-bold">Rating</th>
                                            <th className="px-6 py-5 hidden md:table-cell font-bold">Date</th>
                                            <th className="px-6 py-5 hidden lg:table-cell font-bold">Duration</th>
                                            <th className="px-6 py-5"></th>
                                        </tr>
                                    </thead>

                                    <tbody className="divide-y divide-border/30">
                                        <AnimatePresence>
                                            {paginated.map((match, idx) => (
                                                <MatchRow
                                                    key={match.id || idx}
                                                    match={match}
                                                    onClick={() => setSelectedMatch(match)}
                                                />
                                            ))}
                                        </AnimatePresence>
                                    </tbody>
                                </table>
                            </div>

                            {/* Pagination */}
                            {totalPages > 1 && (
                                <div className="flex justify-center items-center gap-3 py-6 bg-bg-secondary/20 border-t border-border">
                                    <button
                                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                                        disabled={page === 1}
                                        className="p-2 rounded-lg text-text-secondary hover:bg-bg-hover hover:text-text-primary transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                                    >
                                        <ChevronLeft size={20} />
                                    </button>

                                    <div className="flex items-center gap-1">
                                        {Array.from({ length: totalPages }).map((_, i) => {
                                            const pageNum = i + 1;
                                            return (
                                                <button
                                                    key={pageNum}
                                                    onClick={() => setPage(pageNum)}
                                                    className={`w-10 h-10 rounded-lg text-sm font-bold transition-all ${page === pageNum
                                                        ? 'bg-accent text-white shadow-md'
                                                        : 'text-text-secondary hover:bg-bg-hover hover:text-text-primary'
                                                        }`}
                                                >
                                                    {pageNum}
                                                </button>
                                            );
                                        })}
                                    </div>

                                    <button
                                        onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                                        disabled={page === totalPages}
                                        className="p-2 rounded-lg text-text-secondary hover:bg-bg-hover hover:text-text-primary transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                                    >
                                        <ChevronRight size={20} />
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </motion.div>
            </div>

            <MatchDetailModal match={selectedMatch} onClose={() => setSelectedMatch(null)} />
        </div>
    );
}

function MatchRow({ match, onClick }) {
    const eloChange = (match.your_elo_after ?? match.your_elo_before) - match.your_elo_before;
    const isWin = match.result === 'win';
    const isDraw = match.result === 'draw';

    const durationStr = match.duration_seconds
        ? match.duration_seconds >= 60
            ? `${Math.floor(match.duration_seconds / 60)}m ${match.duration_seconds % 60}s`
            : `${match.duration_seconds}s`
        : '—';

    return (
        <tr
            onClick={onClick}
            className="hover:bg-bg-hover/40 transition-colors cursor-pointer group"
        >
            <td className="px-6 py-4">
                <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center text-base font-bold text-accent shrink-0 border border-accent/20 group-hover:scale-105 transition-transform">
                        {match.opponent_username?.charAt(0).toUpperCase() || '?'}
                    </div>
                    <div className="flex flex-col">
                        <span className="font-bold text-text-primary tracking-wide">
                            {match.opponent_username}
                        </span>
                        <span className="text-xs font-medium text-text-muted mt-0.5">
                            {match.opponent_elo} ELO
                        </span>
                    </div>
                </div>
            </td>

            <td className="px-6 py-4">
                <span className={`inline-flex items-center justify-center min-w-[85px] px-3 py-1.5 rounded-md font-bold text-xs uppercase tracking-wider border ${isWin
                    ? 'bg-win/10 text-win border-win/20'
                    : isDraw
                        ? 'bg-draw/10 text-draw border-draw/20'
                        : 'bg-loss/10 text-loss border-loss/20'
                    }`}>
                    {isWin ? 'Victory' : isDraw ? 'Draw' : 'Defeat'}
                </span>
            </td>

            <td className="px-6 py-4">
                <div className="flex flex-col">
                    <div className={`flex items-center gap-1.5 text-base font-bold ${eloChange > 0 ? 'text-win' : eloChange < 0 ? 'text-loss' : 'text-text-muted'
                        }`}>
                        {eloChange > 0 ? <TrendingUp size={16} /> : eloChange < 0 ? <TrendingDown size={16} /> : <Minus size={16} />}
                        <span>{eloChange > 0 ? `+${eloChange}` : eloChange}</span>
                    </div>
                    <span className="text-xs font-medium text-text-muted mt-0.5">
                        {match.your_elo_before} → {match.your_elo_after ?? '—'}
                    </span>
                </div>
            </td>

            <td className="px-6 py-4 hidden md:table-cell">
                <span className="text-sm font-medium text-text-secondary">
                    {match.started_at ? dayjs(match.started_at).format('DD MMM YYYY') : '—'}
                </span>
            </td>

            <td className="px-6 py-4 hidden lg:table-cell">
                <span className="text-sm font-medium text-text-secondary">
                    {durationStr}
                </span>
            </td>

            <td className="px-6 py-4 text-right">
                <ChevronRight size={20} className="text-text-muted group-hover:text-accent group-hover:translate-x-1 transition-all inline-block" />
            </td>
        </tr>
    );
}

function MatchDetailModal({ match, onClose }) {
    if (!match) return null;

    const eloChange = (match.your_elo_after ?? match.your_elo_before) - match.your_elo_before;
    const isWin = match.result === 'win';
    const isDraw = match.result === 'draw';

    const durationStr = match.duration_seconds
        ? match.duration_seconds >= 60
            ? `${Math.floor(match.duration_seconds / 60)}m ${match.duration_seconds % 60}s`
            : `${match.duration_seconds}s`
        : '—';

    return (
        <Modal isOpen={!!match} onClose={onClose} title="Match Details" size="md">
            <div className="space-y-6">
                {/* Result Banner */}
                <div className={`rounded-2xl p-6 text-center shadow-inner ${isWin ? 'bg-win/10 border border-win/20'
                    : isDraw ? 'bg-draw/10 border border-draw/20'
                        : 'bg-loss/10 border border-loss/20'
                    }`}>
                    <Trophy size={32} className={`mx-auto mb-3 ${isWin ? 'text-win' : isDraw ? 'text-draw' : 'text-loss'}`} />
                    <h3 className={`text-2xl font-extrabold tracking-tight ${isWin ? 'text-win' : isDraw ? 'text-draw' : 'text-loss'}`}>
                        {isWin ? 'Victory!' : isDraw ? 'Draw' : 'Defeat'}
                    </h3>
                    <p className="text-xs font-medium text-text-muted mt-2 opacity-80">
                        {match.started_at ? dayjs(match.started_at).format('D MMMM YYYY, HH:mm') : ''}
                    </p>
                </div>

                {/* Details Grid */}
                <div className="grid grid-cols-2 gap-4">
                    <DetailCard icon={User} label="Opponent" value={match.opponent_username} sub={`${match.opponent_elo} ELO`} />
                    <DetailCard
                        icon={eloChange >= 0 ? TrendingUp : TrendingDown}
                        label="Rating Change"
                        value={eloChange > 0 ? `+${eloChange}` : `${eloChange}`}
                        valueColor={eloChange > 0 ? 'text-win' : eloChange < 0 ? 'text-loss' : 'text-text-muted'}
                        sub={`${match.your_elo_before} → ${match.your_elo_after ?? '—'}`}
                    />
                    <DetailCard icon={Clock} label="Duration" value={durationStr} />
                    <DetailCard icon={Calendar} label="Date" value={match.started_at ? dayjs(match.started_at).format('D MMM YYYY') : '—'} />
                </div>
            </div>
        </Modal>
    );
}

function DetailCard({ icon: Icon, label, value, sub, valueColor = 'text-text-primary' }) {
    return (
        <div className="bg-bg-secondary border border-border rounded-xl p-4 hover:border-border-hover transition-colors">
            <div className="flex items-center gap-2 mb-2">
                <Icon size={14} className="text-text-muted" />
                <span className="text-[10px] text-text-muted uppercase tracking-widest font-bold">{label}</span>
            </div>
            <p className={`text-base font-bold ${valueColor}`}>{value}</p>
            {sub && <p className="text-xs font-medium text-text-muted mt-1">{sub}</p>}
        </div>
    );
}