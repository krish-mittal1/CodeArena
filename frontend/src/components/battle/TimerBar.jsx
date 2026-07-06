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
        } catch (err) {
            console.error('Failed to forfeit match:', err);
        } finally {
            setForfeiting(false);
        }
    };

    return (
        <div className="relative flex items-center justify-between px-6 py-2 bg-bg-primary border-b border-border z-20">
            {/* Absolute Progress Bar */}
            <div className="absolute bottom-0 left-0 h-[2px] w-full bg-bg-surface overflow-hidden">
                <div
                    className={`h-full transition-all duration-1000 ease-linear ${isCritical ? 'bg-loss'
                        : isWarning ? 'bg-draw'
                            : 'bg-accent'
                        }`}
                    style={{ width: `${pct}%` }}
                />
            </div>

            {/* Left Zone: Branding & Nav */}
            <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                    <Code2 className="w-5 h-5 text-accent" />
                    <span className="text-sm font-semibold text-text-primary tracking-tight">
                        CodeArena Workspace
                    </span>
                </div>
            </div>

            {/* Center Zone: Battle Timer */}
            <div className="absolute left-1/2 -translate-x-1/2 flex items-center justify-center">
                <div className={`flex items-center gap-2 px-3 py-1 rounded-sm border transition-colors ${isCritical
                    ? 'bg-loss/10 border-loss/50 text-loss'
                    : isWarning
                        ? 'bg-draw/10 border-draw/50 text-draw'
                        : 'bg-bg-elevated border-border text-text-primary'
                    }`}>
                    <Clock className="w-3.5 h-3.5" />
                    <span className="font-mono font-medium text-sm">
                        {formatTime(remainingSeconds)}
                    </span>
                </div>
            </div>

            {/* Right Zone: Profile, Opponent, Actions */}
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-3">
                    {/* User */}
                    {user && (
                        <div className="flex items-center gap-2">
                            <span className="text-sm text-text-primary">{user.username}</span>
                            {user.elo != null && (
                                <span className="text-xs text-text-secondary">
                                    ({user.elo})
                                </span>
                            )}
                        </div>
                    )}

                    <div className="text-text-muted px-1 font-mono text-xs">
                        VS
                    </div>

                    {/* Opponent */}
                    {opponent && (
                        <div className="flex items-center gap-2">
                            <span className="text-sm text-text-secondary">{opponent.username}</span>
                            {opponent.elo != null && (
                                <span className="text-xs text-text-muted">
                                    ({opponent.elo})
                                </span>
                            )}
                            {opponentDisconnected && (
                                <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-draw bg-draw/10 px-1 rounded ml-1">
                                    DC
                                </span>
                            )}
                        </div>
                    )}
                </div>

                <div className="w-px h-4 bg-border mx-1"></div>

                <button
                    type="button"
                    onClick={handleForfeit}
                    disabled={!!matchResult || forfeiting}
                    className="flex items-center gap-1.5 px-3 py-1 rounded-sm text-xs font-medium bg-bg-surface border border-border text-text-secondary hover:text-loss hover:border-loss transition-colors disabled:opacity-50 disabled:cursor-not-allowed group"
                >
                    <LogOut className="w-3.5 h-3.5" />
                    {forfeiting ? 'Leaving' : 'Leave Match'}
                </button>
            </div>
        </div>
    );
}
