import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import {
    History as HistoryIcon, Filter, ChevronLeft, ChevronRight, Swords,
    Calendar, Trophy, Clock, TrendingUp, User,
} from 'lucide-react';
import dayjs from 'dayjs';
import { useAuthStore } from '../stores/authStore';
import { matchApi } from '../api/auth';
import Button from '../components/ui/Button';
import Modal from '../components/ui/Modal';
import EmptyState from '../components/ui/EmptyState';
import { TableRowSkeleton } from '../components/ui/Skeleton';

const ITEMS_PER_PAGE = 10;

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
        <div className="min-h-screen bg-bg-root">
            <div className="w-full px-6 sm:px-10 lg:px-12 pt-12 pb-24">

                {/* Header & Filters */}
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col xl:flex-row xl:items-center justify-between gap-6 mb-10">
                    <div className="flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-6">
                        <h1 className="text-4xl sm:text-5xl font-extrabold text-text-primary flex items-center gap-4 tracking-tight">
                            <HistoryIcon size={38} className="text-accent" />
                            Match History
                        </h1>
                        <div className="h-10 w-px bg-border hidden sm:block"></div>
                        <p className="text-lg text-text-muted font-medium">
                            {filtered.length} {filtered.length === 1 ? 'match' : 'matches'} found
                        </p>
                    </div>

                    <div className="flex items-center gap-4 flex-wrap">
                        <div className="flex items-center gap-2 text-lg text-text-muted font-medium">
                            <Filter size={20} />
                            <span>Filter:</span>
                        </div>
                        <div className="flex items-center gap-2">
                            {['all', 'win', 'loss', 'draw'].map((val) => (
                                <button
                                    key={val}
                                    onClick={() => { setFilterResult(val); setPage(1); }}
                                    className={`px-6 py-2.5 text-base font-semibold capitalize rounded-full border transition-all ${filterResult === val
                                        ? 'bg-accent/15 text-accent border-accent/40 shadow-sm'
                                        : 'bg-transparent border-border text-text-muted hover:text-text-primary hover:border-accent/40'
                                        }`}
                                >
                                    {val}
                                </button>
                            ))}
                        </div>
                    </div>
                </motion.div>

                {/* Table */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="rounded-xl border border-border bg-bg-elevated"
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
                        <div className="py-20 text-center">
                            <p className="text-loss text-sm font-medium">Failed to load match history</p>
                        </div>
                    ) : filtered.length === 0 ? (
                        <EmptyState
                            icon={Swords}
                            title="No matches found"
                            description="Play some matches to see your history."
                        />
                    ) : (
                        <>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">

                                    <thead className="text-sm uppercase tracking-wider text-text-muted border-b border-border">
                                        <tr>
                                            <th className="px-6 py-6 text-left font-semibold">Opponent</th>
                                            <th className="px-6 py-6 text-left font-semibold">Result</th>
                                            <th className="px-6 py-6 text-left font-semibold">Rating</th>
                                            <th className="px-6 py-6 text-left hidden md:table-cell font-semibold">Date</th>
                                            <th className="px-6 py-6 text-left hidden lg:table-cell font-semibold">Duration</th>
                                            <th className="px-6 py-6"></th>
                                        </tr>
                                    </thead>

                                    <tbody>
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

                            {totalPages > 1 && (
                                <div className="flex justify-center items-center gap-2 py-6 border-t border-border">
                                    <Button
                                        variant="secondary"
                                        size="sm"
                                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                                        disabled={page === 1}
                                    >
                                        <ChevronLeft size={14} />
                                    </Button>

                                    {Array.from({ length: totalPages }).map((_, i) => {
                                        const pageNum = i + 1;
                                        return (
                                            <button
                                                key={pageNum}
                                                onClick={() => setPage(pageNum)}
                                                className={`w-8 h-8 rounded-md text-xs font-medium transition ${page === pageNum
                                                    ? 'bg-accent/20 text-accent border border-accent/30'
                                                    : 'text-text-muted hover:bg-bg-hover'
                                                    }`}
                                            >
                                                {pageNum}
                                            </button>
                                        );
                                    })}

                                    <Button
                                        variant="secondary"
                                        size="sm"
                                        onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                                        disabled={page === totalPages}
                                    >
                                        <ChevronRight size={14} />
                                    </Button>
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
            className="border-b border-border hover:bg-bg-hover transition cursor-pointer group"
        >
            <td className="px-6 py-7">
                <div className="flex items-center gap-5">
                    <div className="w-12 h-12 rounded-full bg-accent/15 flex items-center justify-center text-lg font-bold text-accent shrink-0">
                        {match.opponent_username?.charAt(0).toUpperCase() || '?'}
                    </div>
                    <div>
                        <div className="text-lg font-semibold text-text-primary group-hover:text-accent transition-colors">
                            {match.opponent_username}
                        </div>
                        <div className="text-base text-text-muted mt-1 font-medium">
                            {match.opponent_elo} ELO
                        </div>
                    </div>
                </div>
            </td>

            <td className="px-6 py-7">
                <span className={`text-base px-6 py-2.5 rounded-full font-bold border flex w-fit items-center justify-center min-w-[100px] text-center ${isWin
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                    : isDraw
                        ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30'
                        : 'bg-red-500/10 text-red-400 border-red-500/30'
                    }`}>
                    {isWin ? 'Win' : isDraw ? 'Draw' : 'Loss'}
                </span>
            </td>

            <td className="px-6 py-7">
                <div className={`text-lg font-bold tracking-wide ${eloChange > 0 ? 'text-win' : eloChange < 0 ? 'text-loss' : 'text-text-muted'}`}>
                    {eloChange > 0 ? `+${eloChange}` : eloChange}
                </div>
                <div className="text-base text-text-muted mt-1 font-medium">
                    {match.your_elo_before} → {match.your_elo_after ?? '—'}
                </div>
            </td>

            <td className="px-6 py-7 hidden md:table-cell text-lg font-medium text-text-secondary">
                {match.started_at ? dayjs(match.started_at).format('D MMM YYYY') : '—'}
            </td>

            <td className="px-6 py-7 hidden lg:table-cell text-lg text-text-muted font-mono font-medium">
                {durationStr}
            </td>

            <td className="px-6 py-7 text-right">
                <ChevronRight size={20} className="text-text-muted group-hover:text-accent transition-colors" />
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
                <div className={`rounded-xl p-5 text-center ${isWin ? 'bg-win/10 border border-win/20' : isDraw ? 'bg-draw/10 border border-draw/20' : 'bg-loss/10 border border-loss/20'
                    }`}>
                    <Trophy size={28} className={`mx-auto mb-2 ${isWin ? 'text-win' : isDraw ? 'text-draw' : 'text-loss'}`} />
                    <h3 className={`text-2xl font-extrabold ${isWin ? 'text-win' : isDraw ? 'text-draw' : 'text-loss'}`}>
                        {isWin ? 'Victory!' : isDraw ? 'Draw' : 'Defeat'}
                    </h3>
                    <p className="text-xs text-text-muted mt-1">
                        {match.started_at ? dayjs(match.started_at).format('D MMMM YYYY, HH:mm') : ''}
                    </p>
                </div>

                {/* Details Grid */}
                <div className="grid grid-cols-2 gap-3">
                    <DetailCard icon={User} label="Opponent" value={match.opponent_username} sub={`${match.opponent_elo} ELO`} />
                    <DetailCard
                        icon={TrendingUp}
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
        <div className="bg-bg-surface/80 rounded-xl p-3.5">
            <div className="flex items-center gap-2 mb-1.5">
                <Icon size={13} className="text-text-muted" />
                <span className="text-[11px] text-text-muted uppercase tracking-wider font-medium">{label}</span>
            </div>
            <p className={`text-sm font-bold ${valueColor}`}>{value}</p>
            {sub && <p className="text-[11px] text-text-muted mt-0.5">{sub}</p>}
        </div>
    );
}