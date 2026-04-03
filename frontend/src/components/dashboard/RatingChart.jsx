import { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts';
import { TrendingUp, Swords as SwordsIcon } from 'lucide-react';
import dayjs from 'dayjs';

export default function RatingChart({ history = [], currentElo = 0 }) {
    const data = useMemo(() => {
        if (!history.length) return [];

        const sorted = [...history].sort(
            (a, b) => new Date(a.started_at) - new Date(b.started_at)
        );

        return sorted.map((match, i) => ({
            label: `MATCH ${i + 1}`,
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
            <div className="db-chart paper-card grain-panel">
                <h3 className="db-section-title mb-6">RATING PROGRESSION</h3>
                <div className="flex flex-col items-center justify-center py-16 text-center">
                    <SwordsIcon size={32} className="text-text-muted/30 mb-3" />
                    <p className="text-sm text-text-secondary font-medium">No rating data yet</p>
                    <p className="text-xs text-text-muted mt-1">Play matches to see your ELO graph</p>
                </div>
            </div>
        );
    }

    const allElos = data.map((d) => d.elo);
    const minElo = Math.min(...allElos) - 40;
    const maxElo = Math.max(...allElos) + 40;
    const baselineElo = data[0]?.eloBefore ?? 0;

    /* Show ~4 tick labels using interval */
    const tickInterval = data.length <= 6 ? 0 : Math.floor(data.length / 4);

    return (
        <div className="db-chart paper-card grain-panel">
            <div className="db-chart__header">
                <h3 className="db-section-title">RATING PROGRESSION</h3>
                <div className="db-chart__legend">
                    <span className="db-chart__dot" />
                    <span className="text-xs text-text-muted font-mono tracking-wider">CURRENT ELO</span>
                </div>
            </div>

            <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={data} margin={{ top: 10, right: 12, left: -18, bottom: 5 }}>
                    <defs>
                        <linearGradient id="eloGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="var(--color-accent)" stopOpacity={0.3} />
                            <stop offset="100%" stopColor="var(--color-accent)" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="var(--color-border)"
                        strokeOpacity={0.4}
                        vertical={false}
                    />
                    <XAxis
                        dataKey="label"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: 'var(--color-text-muted)', fontSize: 10, fontFamily: 'var(--font-mono)' }}
                        interval={tickInterval}
                    />
                    <YAxis
                        domain={[minElo, maxElo]}
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: 'var(--color-text-muted)', fontSize: 10, fontFamily: 'var(--font-mono)' }}
                    />
                    {baselineElo > 0 && (
                        <ReferenceLine
                            y={baselineElo}
                            stroke="var(--color-text-muted)"
                            strokeDasharray="6 4"
                            strokeOpacity={0.3}
                        />
                    )}
                    <Tooltip content={<ChartTooltip />} cursor={{ stroke: 'var(--color-accent)', strokeWidth: 1, strokeDasharray: '4 4' }} />
                    <Area
                        type="monotone"
                        dataKey="elo"
                        stroke="var(--color-accent)"
                        strokeWidth={2.5}
                        fill="url(#eloGrad)"
                        dot={false}
                        activeDot={{
                            r: 5,
                            fill: 'var(--color-accent)',
                            stroke: 'var(--color-bg-primary)',
                            strokeWidth: 3,
                        }}
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
        <div className="db-tooltip">
            <p className="text-[10px] text-text-muted font-mono tracking-wider mb-1">{d.fullDate}</p>
            <p className="text-base font-bold text-text-primary mb-1">{d.elo} ELO</p>
            <div className="flex items-center justify-between text-xs gap-4">
                <span className="text-text-secondary">vs {d.opponent}</span>
                <span className={`font-mono font-bold ${change > 0 ? 'text-win' : change < 0 ? 'text-loss' : 'text-text-muted'}`}>
                    {change > 0 ? `+${change}` : change}
                </span>
            </div>
        </div>
    );
}
