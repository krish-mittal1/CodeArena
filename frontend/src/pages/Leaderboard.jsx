import { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Trophy, Medal, Crown } from 'lucide-react';
import { leaderboardApi } from '../api/auth';
import { formatElo } from '../utils/formatters';
import { TableRowSkeleton } from '../components/ui/Skeleton';

const TABS = [
    { id: 'all_time', label: 'All-Time ELO' },
    { id: 'weekly', label: 'Weekly Wins' },
];

function RankIcon({ rank }) {
    if (rank === 1) return <Crown size={18} className="text-yellow-400" />;
    if (rank === 2) return <Medal size={18} className="text-gray-300" />;
    if (rank === 3) return <Medal size={18} className="text-amber-600" />;
    return <span className="text-text-muted font-mono text-sm w-[18px] text-center">{rank}</span>;
}

export default function Leaderboard() {
    const [period, setPeriod] = useState('all_time');

    const { data, isLoading, isError } = useQuery({
        queryKey: ['leaderboard', period],
        queryFn: () => leaderboardApi.get(period, 100),
        staleTime: 60_000,
    });

    const entries = data?.entries || [];

    return (
        <div className="min-h-[calc(100vh-64px)] bg-bg-root">
            <div className="max-w-3xl mx-auto px-6 py-10">
                <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center border border-accent/20">
                            <Trophy size={24} className="text-accent" />
                        </div>
                        <div>
                            <p className="editorial-kicker mb-1">Global rankings</p>
                            <h1 className="text-2xl font-bold text-text-primary">Leaderboard</h1>
                        </div>
                    </div>

                    <div className="flex gap-2">
                        {TABS.map((tab) => (
                            <button
                                key={tab.id}
                                type="button"
                                onClick={() => setPeriod(tab.id)}
                                className={`px-4 py-2 text-sm font-medium border transition-colors ${
                                    period === tab.id
                                        ? 'bg-accent text-white border-accent'
                                        : 'border-border text-text-secondary hover:text-text-primary'
                                }`}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </div>
                </motion.div>

                <div className="paper-card grain-panel overflow-hidden">
                    {isLoading ? (
                        <div className="p-4 space-y-3">
                            {Array.from({ length: 10 }).map((_, i) => (
                                <TableRowSkeleton key={i} />
                            ))}
                        </div>
                    ) : isError ? (
                        <p className="p-8 text-center text-loss text-sm">Failed to load leaderboard</p>
                    ) : entries.length === 0 ? (
                        <p className="p-8 text-center text-text-muted text-sm">No rankings yet</p>
                    ) : (
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-border text-text-muted text-xs uppercase tracking-wider">
                                    <th className="text-left py-3 px-4 font-semibold">Rank</th>
                                    <th className="text-left py-3 px-4 font-semibold">Player</th>
                                    <th className="text-right py-3 px-4 font-semibold">ELO</th>
                                    <th className="text-right py-3 px-4 font-semibold hidden sm:table-cell">
                                        {period === 'weekly' ? 'Wins (7d)' : 'Wins'}
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {entries.map((row) => (
                                    <tr key={row.user_id} className="border-b border-border/50 hover:bg-bg-hover/50">
                                        <td className="py-3 px-4">
                                            <div className="flex items-center justify-center w-8">
                                                <RankIcon rank={row.rank} />
                                            </div>
                                        </td>
                                        <td className="py-3 px-4 font-medium text-text-primary">
                                            {row.username}
                                        </td>
                                        <td className="py-3 px-4 text-right font-mono text-accent">
                                            {formatElo(row.elo)}
                                        </td>
                                        <td className="py-3 px-4 text-right text-text-secondary hidden sm:table-cell">
                                            {period === 'weekly' ? row.weekly_wins : row.matches_won}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}
