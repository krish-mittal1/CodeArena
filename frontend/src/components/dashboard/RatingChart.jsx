import { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { TrendingUp, Swords as SwordsIcon } from 'lucide-react';
import dayjs from 'dayjs';

export default function RatingChart({ history = [], currentElo = 0 }) {
    const data = useMemo(() => {
        if (!history.length) return [];

        // Sort oldest → newest by started_at
        const sorted = [...history].sort(
            (a, b) => new Date(a.started_at) - new Date(b.started_at)
        );

        return sorted.map((match) => ({
            date: dayjs(match.started_at).format('D MMM'),
            fullDate: dayjs(match.started_at).format('D MMM YYYY, HH:mm'),
            elo: match.your_elo_after ?? match.your_elo_before,
            eloBefore: match.your_elo_before,
            opponent: match.opponent_username,
            result: match.result,
            change: (match.your_elo_after ?? match.your_elo_before) - match.your_elo_before,
        }));
    }, [history]);

    if (data.length === 0) {
        return (
            <div className="bg-bg-secondary border border-border rounded-xl p-6">
                <h3 className="text-lg font-semibold text-text-primary flex items-center gap-2 mb-6">
                    <TrendingUp size={18} className="text-accent" />
                    Rating Progression
                </h3>
                <div className="flex flex-col items-center justify-center py-12 text-center">
                    <SwordsIcon size={32} className="text-text-muted mb-3" />
                    <p className="text-sm text-text-secondary">No rating data yet</p>
                    <p className="text-xs text-text-muted mt-1">Play matches to see your ELO graph</p>
                </div>
            </div>
        );
    }

    const allElos = data.map((d) => d.elo);
    const minElo = Math.min(...allElos) - 50;
    const maxElo = Math.max(...allElos) + 50;

    return (
        <div className="bg-bg-secondary border border-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-text-primary flex items-center gap-2">
                    <TrendingUp size={18} className="text-accent" />
                    Rating Progression
                </h3>
                <div className="flex items-center gap-2">
                    <span className="text-xs text-text-muted">{data.length} matches</span>
                    <span className="text-sm font-mono text-accent font-bold">{currentElo} ELO</span>
                </div>
            </div>

            <ResponsiveContainer width="100%" height={260}>
                <AreaChart data={data} margin={{ top: 5, right: 10, left: -15, bottom: 5 }}>
                    <defs>
                        <linearGradient id="eloGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.35} />
                            <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#30363d" vertical={false} />
                    <XAxis
                        dataKey="date"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#484f58', fontSize: 11 }}
                        interval="preserveStartEnd"
                    />
                    <YAxis
                        domain={[minElo, maxElo]}
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#484f58', fontSize: 11 }}
                    />
                    <Tooltip content={<ChartTooltip />} cursor={{ stroke: '#3b82f6', strokeWidth: 1, strokeDasharray: '4 4' }} />
                    <Area
                        type="monotone"
                        dataKey="elo"
                        stroke="#3b82f6"
                        strokeWidth={2.5}
                        fill="url(#eloGradient)"
                        dot={false}
                        activeDot={{ r: 5, fill: '#3b82f6', stroke: '#1c2333', strokeWidth: 3 }}
                        isAnimationActive={true}
                        animationDuration={1200}
                        animationEasing="ease-out"
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}

function ChartTooltip({ active, payload }) {
    if (!active || !payload?.length) return null;
    const d = payload[0].payload;
    const change = d.change;
    return (
        <div className="bg-bg-surface/95 backdrop-blur-md border border-border rounded-xl px-4 py-3 shadow-2xl min-w-[180px]">
            <p className="text-xs text-text-muted mb-1.5">{d.fullDate}</p>
            <p className="text-base font-bold text-text-primary mb-1">{d.elo} ELO</p>
            <div className="flex items-center justify-between text-xs">
                <span className="text-text-secondary">vs {d.opponent}</span>
                <span className={`font-mono font-bold ${change > 0 ? 'text-win' : change < 0 ? 'text-loss' : 'text-text-muted'
                    }`}>
                    {change > 0 ? `+${change}` : change}
                </span>
            </div>
        </div>
    );
}
