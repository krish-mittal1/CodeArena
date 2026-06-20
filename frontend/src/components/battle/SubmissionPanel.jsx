import { useBattleStore } from '../../stores/battleStore';
import { VERDICTS } from '../../utils/constants';
import { Activity, History, ServerCrash, CheckCircle2, XCircle, Clock } from 'lucide-react';

export default function SubmissionPanel() {
    const submissionHistory = useBattleStore((s) => s.submissionHistory);
    const submissionStatus = useBattleStore((s) => s.submissionStatus);
    const opponentActivity = useBattleStore((s) => s.opponentActivity);

    return (
        <div className="flex flex-col h-56 bg-bg-root border-t border-border z-20 shrink-0 relative">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-2 bg-bg-primary border-b border-border shrink-0">
                <div className="flex items-center gap-2">
                    {submissionStatus === 'running' || submissionStatus === 'submitting' ? (
                        <>
                            <div className="w-3.5 h-3.5 rounded-full border-2 border-accent border-t-transparent animate-spin" />
                            <span className="text-xs font-semibold text-accent tracking-wide">Evaluating</span>
                        </>
                    ) : (
                        <>
                            <Activity className="w-3.5 h-3.5 text-text-secondary" />
                            <span className="text-xs font-semibold text-text-primary tracking-wide">Output</span>
                        </>
                    )}
                </div>
                <span className="text-[10px] font-mono text-text-muted bg-bg-surface px-1.5 py-0.5 rounded-sm border border-border">
                    {submissionHistory.length} RUNS
                </span>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
                {submissionHistory.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-text-muted gap-2">
                        <span className="text-xs font-mono">No submissions yet.</span>
                    </div>
                ) : (
                    [...submissionHistory].reverse().map((sub, i) => {
                        const v = VERDICTS[sub.verdict] || VERDICTS.queued;
                        // CI-like compact colored rows based on verdict
                        const isSuccess = sub.verdict === 'accepted';
                        const isQueuedOrRunning = sub.verdict === 'queued' || sub.verdict === 'running';
                        const isError = !isSuccess && !isQueuedOrRunning;

                        const rowColor = isSuccess ? 'border-l-win bg-win/5 border-border' :
                                         isError ? 'border-l-loss bg-loss/5 border-border' :
                                         'border-l-border bg-bg-surface border-border';

                        const textColor = isSuccess ? 'text-win' : isError ? 'text-loss' : 'text-text-secondary';

                        return (
                            <div key={i} className={`flex items-center justify-between px-3 py-2 border-y border-r border-l-[3px] ${rowColor} transition-colors hover:brightness-110 font-mono text-xs`}>
                                <div className="flex items-center gap-2">
                                    <span className={`${textColor} font-bold tracking-wide`}>[{v.label.toUpperCase()}]</span>
                                </div>
                                <div className="flex items-center gap-4 text-text-muted opacity-90">
                                    {sub.time_ms != null && (
                                        <span className="flex items-center gap-1">
                                            {sub.time_ms}ms
                                        </span>
                                    )}
                                    {sub.memory_mb != null && (
                                        <span>{sub.memory_mb}MB</span>
                                    )}
                                    {sub.passed_count != null && sub.total_count != null && (
                                        <span className={`px-1.5 py-0.5 rounded-sm whitespace-nowrap bg-bg-elevated ${textColor}`}>
                                            {isSuccess || isQueuedOrRunning
                                                ? `${sub.passed_count}/${sub.total_count}`
                                                : `FAIL @ ${sub.passed_count + 1}`
                                            }
                                        </span>
                                    )}
                                </div>
                            </div>
                        );
                    })
                )}
            </div>

            {/* Opponent Tracker */}
            {opponentActivity && (
                <div className="absolute top-2 right-4 transform z-50">
                    <div className="flex items-center gap-2 bg-bg-elevated border border-border px-2 py-1 rounded-sm shadow-sm">
                        <Activity className="w-3 h-3 text-text-muted" />
                        <span className="text-[10px] font-mono tracking-wide text-text-secondary">
                            opponent:
                            <span className="ml-1 text-text-primary">
                                {opponentActivity.verdict ? (VERDICTS[opponentActivity.verdict]?.label || opponentActivity.verdict).toLowerCase() : 'submitted'}
                            </span>
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
}
