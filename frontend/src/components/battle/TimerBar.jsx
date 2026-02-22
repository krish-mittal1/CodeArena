import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useBattleStore } from '../../stores/battleStore';
import { useAuthStore } from '../../stores/authStore';
import { useTimer } from '../../hooks/useTimer';
import { formatTime } from '../../utils/formatters';
import { matchApi } from '../../api/auth';
import { Swords, LogOut, Code2, Clock, Shield, ShieldAlert } from 'lucide-react';

export default function TimerBar() {
    const { remainingSeconds } = useTimer();
    const duration = useBattleStore((s) => s.duration);
    const matchId = useBattleStore((s) => s.matchId);
    const opponent = useBattleStore((s) => s.opponent);
    const opponentDisconnected = useBattleStore((s) => s.opponentDisconnected);
    const matchResult = useBattleStore((s) => s.matchResult);
    const user = useAuthStore((s) => s.user);
    const [forfeiting, setForfeiting] = useState(false);

    const pct = duration > 0 ? (remainingSeconds / duration) * 100 : 0;
    const isWarning = remainingSeconds <= 120 && remainingSeconds > 30;
    const isCritical = remainingSeconds <= 30;

    const handleForfeit = async () => {
        if (!matchId || matchResult || forfeiting) return;

        const confirmed = window.confirm(
            'Are you sure you want to leave? This counts as a loss and will affect your ELO.'
        );
        if (!confirmed) return;

        setForfeiting(true);
        try {
            await matchApi.forfeit(matchId);
            // MATCH_ENDED WS event will drive UI updates
        } catch (err) {
            console.error('Failed to forfeit match:', err);
            setForfeiting(false);
        }
    };

    return (
        <div className="relative flex items-center justify-between px-6 py-3 bg-slate-950 border-b border-slate-800 shadow-sm z-20">
            {/* Absolute Progress Bar */}
            <div className="absolute bottom-0 left-0 h-[2px] w-full bg-slate-900 overflow-hidden">
                <div
                    className={`h-full transition-all duration-1000 ease-linear ${isCritical ? 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.8)]'
                        : isWarning ? 'bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.8)]'
                            : 'bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.8)]'
                        }`}
                    style={{ width: `${pct}%` }}
                />
            </div>

            {/* Left Zone: Branding & Nav */}
            <div className="flex items-center gap-8">
                <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-indigo-500/10 rounded-lg border border-indigo-500/20">
                        <Code2 className="w-5 h-5 text-indigo-400" />
                    </div>
                    <span className="text-xl font-bold text-white tracking-tight">
                        CodeArena
                    </span>
                </div>
            </div>

            {/* Center Zone: Battle Timer */}
            <div className="absolute left-1/2 -translate-x-1/2 flex items-center justify-center">
                <div className={`flex items-center gap-2 px-5 py-1.5 rounded-full border shadow-sm backdrop-blur-md transition-colors ${isCritical
                    ? 'bg-red-500/10 border-red-500/50 text-red-400 animate-pulse'
                    : isWarning
                        ? 'bg-amber-500/10 border-amber-500/50 text-amber-400'
                        : 'bg-slate-900/50 border-slate-700/50 text-slate-200'
                    }`}>
                    <Clock className="w-4 h-4" />
                    <span className="font-mono font-bold tracking-wider text-base">
                        {formatTime(remainingSeconds)}
                    </span>
                </div>
            </div>

            {/* Right Zone: Profile, Opponent, Actions */}
            <div className="flex items-center gap-6">
                <div className="flex items-center gap-4 bg-slate-900/50 rounded-lg p-1.5 border border-slate-800">
                    {/* User */}
                    {user && (
                        <div className="flex items-center gap-2 px-3 py-1 rounded-md bg-slate-800/80 border border-slate-700/50">
                            <span className="text-sm font-medium text-white">{user.username}</span>
                            {user.elo != null && (
                                <span className="text-xs font-bold text-indigo-400 bg-indigo-500/10 px-1.5 py-0.5 rounded">
                                    {user.elo}
                                </span>
                            )}
                        </div>
                    )}

                    <div className="text-slate-500 px-1">
                        <Swords className="w-4 h-4" />
                    </div>

                    {/* Opponent */}
                    {opponent && (
                        <div className="flex items-center gap-2 px-3 py-1 rounded-md bg-slate-800/40 border border-slate-700/30">
                            <span className="text-sm font-medium text-slate-300">{opponent.username}</span>
                            {opponent.elo != null && (
                                <span className="text-xs font-bold text-rose-400 bg-rose-500/10 px-1.5 py-0.5 rounded">
                                    {opponent.elo}
                                </span>
                            )}
                            {opponentDisconnected && (
                                <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-amber-500 bg-amber-500/10 px-1.5 py-0.5 rounded ml-1">
                                    <ShieldAlert className="w-3 h-3" /> DC
                                </span>
                            )}
                        </div>
                    )}
                </div>

                <button
                    type="button"
                    onClick={handleForfeit}
                    disabled={!!matchResult || forfeiting}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold border border-rose-500/30 text-rose-400 hover:bg-rose-500 hover:text-white hover:border-rose-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
                >
                    <LogOut className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
                    {forfeiting ? 'Leaving...' : 'Leave Match'}
                </button>
            </div>
        </div>
    );
}
