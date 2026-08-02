import { useState } from 'react';
import { useBattleStore } from '../../stores/battleStore';
import { useAuthStore } from '../../stores/authStore';
import { useTimer } from '../../hooks/useTimer';
import { formatTime } from '../../utils/formatters';
import { matchApi } from '../../api/auth';
import { LogOut, Code2, Clock } from 'lucide-react';

export default function TimerBar() {
    const { remainingSeconds } = useTimer();
    const duration = useBattleStore((s) => s.duration);
    const matchId = useBattleStore((s) => s.matchId);
    const opponent = useBattleStore((s) => s.opponent);
    const opponentDisconnected = useBattleStore((s) => s.opponentDisconnected);
    const matchResult = useBattleStore((s) => s.matchResult);
    const problems = useBattleStore((s) => s.problems);
    const solvedProblemIds = useBattleStore((s) => s.solvedProblemIds);
    const user = useAuthStore((s) => s.user);
    const [forfeiting, setForfeiting] = useState(false);

    const pct = duration > 0 ? (remainingSeconds / duration) * 100 : 0;
    const isWarning = remainingSeconds <= 120 && remainingSeconds > 30;
    const isCritical = remainingSeconds <= 30;
    const totalProblems = problems.length || 1;
    const solvedCount = solvedProblemIds.length;

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
        <div className="relative flex items-center justify-between gap-2 px-3 sm:px-6 py-2 bg-bg-primary border-b border-border z-20 shrink-0 min-h-[44px]">
            <div className="absolute bottom-0 left-0 h-[2px] w-full bg-bg-surface overflow-hidden">
                <div
                    className={`h-full transition-all duration-1000 ease-linear ${isCritical ? 'bg-loss'
                        : isWarning ? 'bg-draw'
                            : 'bg-accent'
                        }`}
                    style={{ width: `${pct}%` }}
                />
            </div>

            {/* Left: brand (sm+) or compact icon */}
            <div className="flex items-center gap-2 min-w-0 shrink">
                <Code2 className="w-5 h-5 text-accent shrink-0" />
                <span className="hidden sm:inline text-sm font-semibold text-text-primary tracking-tight truncate">
                    CodeArena Workspace
                </span>
            </div>

            {/* Center: timer + progress */}
            <div className="flex items-center justify-center gap-2 sm:gap-3 shrink-0">
                <div className={`flex items-center gap-2 px-2.5 sm:px-3 py-1 rounded-sm border transition-colors ${isCritical
                    ? 'bg-loss/10 border-loss/50 text-loss'
                    : isWarning
                        ? 'bg-draw/10 border-draw/50 text-draw'
                        : 'bg-bg-elevated border-border text-text-primary'
                    }`}>
                    <Clock className="w-3.5 h-3.5" />
                    <span className="font-mono font-medium text-sm tabular-nums">
                        {formatTime(remainingSeconds)}
                    </span>
                </div>
                {totalProblems > 1 && (
                    <div
                        className="flex items-center gap-1 px-2 py-1 rounded-sm border border-border bg-bg-elevated text-xs font-mono tabular-nums text-text-secondary"
                        title={`${solvedCount} of ${totalProblems} problems solved`}
                    >
                        <span className={solvedCount > 0 ? 'text-win' : ''}>{solvedCount}</span>
                        <span className="text-text-muted">/</span>
                        <span>{totalProblems}</span>
                    </div>
                )}
            </div>

            {/* Right: players + leave */}
            <div className="flex items-center gap-2 sm:gap-4 min-w-0">
                <div className="hidden md:flex items-center gap-3 min-w-0">
                    {user && (
                        <div className="flex items-center gap-1.5 min-w-0">
                            <span className="text-sm text-text-primary truncate max-w-[80px] lg:max-w-none">{user.username}</span>
                            {user.elo != null && (
                                <span className="text-xs text-text-secondary shrink-0">
                                    ({user.elo})
                                </span>
                            )}
                        </div>
                    )}

                    <div className="text-text-muted px-1 font-mono text-xs shrink-0">
                        VS
                    </div>

                    {opponent && (
                        <div className="flex items-center gap-1.5 min-w-0">
                            <span className="text-sm text-text-secondary truncate max-w-[80px] lg:max-w-none">{opponent.username}</span>
                            {opponent.elo != null && (
                                <span className="text-xs text-text-muted shrink-0">
                                    ({opponent.elo})
                                </span>
                            )}
                            {opponentDisconnected && (
                                <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-draw bg-draw/10 px-1 rounded shrink-0">
                                    DC
                                </span>
                            )}
                        </div>
                    )}
                </div>

                {/* Compact opponent hint on small screens */}
                {opponent && (
                    <span className="md:hidden text-[11px] text-text-muted truncate max-w-[72px]" title={opponent.username}>
                        vs {opponent.username}
                    </span>
                )}

                <div className="hidden sm:block w-px h-4 bg-border shrink-0" />

                <button
                    type="button"
                    onClick={handleForfeit}
                    disabled={!!matchResult || forfeiting}
                    className="flex items-center gap-1.5 px-2 sm:px-3 py-1.5 min-h-[36px] rounded-sm text-xs font-medium bg-bg-surface border border-border text-text-secondary hover:text-loss hover:border-loss transition-colors disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
                    title={forfeiting ? 'Leaving' : 'Leave Match'}
                >
                    <LogOut className="w-3.5 h-3.5" />
                    <span className="hidden sm:inline">{forfeiting ? 'Leaving' : 'Leave Match'}</span>
                </button>
            </div>
        </div>
    );
}
