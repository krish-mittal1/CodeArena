import { useBattleStore } from '../../stores/battleStore';
import { VERDICTS } from '../../utils/constants';
import { RunCaseBlocks } from '../dsa/ExampleBlocks';
import { Activity } from 'lucide-react';

export default function SubmissionPanel() {
    const submissionHistory = useBattleStore((s) => s.submissionHistory);
    const submissionStatus = useBattleStore((s) => s.submissionStatus);
    const opponentActivity = useBattleStore((s) => s.opponentActivity);
    const runResult = useBattleStore((s) => s.runResult);
    const runStatus = useBattleStore((s) => s.runStatus);
    const problem = useBattleStore((s) => s.problem);
    const clearRunResult = useBattleStore((s) => s.clearRunResult);

    const showSampleRun = runResult && (runStatus === 'running' || runStatus === 'done' || runStatus === 'error');

    return (
        <div className="flex flex-col h-40 sm:h-48 md:h-64 bg-bg-root border-t border-border z-20 shrink-0 relative">
            <div className="flex items-center justify-between px-3 sm:px-4 py-2 bg-bg-primary border-b border-border shrink-0 gap-2">
                <div className="flex items-center gap-2 min-w-0">
                    {runStatus === 'running' ? (
                        <>
                            <div className="w-3.5 h-3.5 rounded-full border-2 border-accent border-t-transparent animate-spin shrink-0" />
                            <span className="text-xs font-semibold text-accent tracking-wide">Running samples</span>
                        </>
                    ) : submissionStatus === 'running' || submissionStatus === 'submitting' ? (
                        <>
                            <div className="w-3.5 h-3.5 rounded-full border-2 border-accent border-t-transparent animate-spin shrink-0" />
                            <span className="text-xs font-semibold text-accent tracking-wide">Evaluating</span>
                        </>
                    ) : (
                        <>
                            <Activity className="w-3.5 h-3.5 text-text-secondary shrink-0" />
                            <span className="text-xs font-semibold text-text-primary tracking-wide">
                                {showSampleRun ? 'Sample run' : 'Output'}
                            </span>
                        </>
                    )}
                </div>
                <div className="flex items-center gap-2 shrink-0">
                    {showSampleRun && (
                        <button
                            type="button"
                            onClick={clearRunResult}
                            className="text-[10px] font-mono text-text-muted hover:text-text-secondary px-1.5 py-0.5 rounded-sm border border-border"
                        >
                            Clear
                        </button>
                    )}
                    <span className="text-[10px] font-mono text-text-muted bg-bg-surface px-1.5 py-0.5 rounded-sm border border-border">
                        {submissionHistory.length} RUNS
                    </span>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto overflow-x-hidden px-3 sm:px-4 py-3 space-y-2 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
                {showSampleRun ? (
                    <div className="space-y-3">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                            <span
                                className="text-sm font-bold"
                                style={{ color: VERDICTS[runResult.status]?.color || 'var(--text-primary)' }}
                            >
                                Run: {VERDICTS[runResult.status]?.label || runResult.status}
                            </span>
                            <span className="text-xs font-mono text-text-secondary">
                                {runResult.passed_test_cases ?? 0}/{runResult.total_test_cases ?? 0} sample cases
                            </span>
                        </div>
                        {runResult.message && (
                            <p className="text-xs text-loss">{runResult.message}</p>
                        )}
                        {runResult.cases?.length > 0 && (
                            <RunCaseBlocks cases={runResult.cases} problem={problem} />
                        )}
                    </div>
                ) : submissionHistory.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-text-muted gap-2">
                        <span className="text-xs font-mono text-center px-2">
                            No submissions yet. Use Run for samples, Submit to judge.
                        </span>
                    </div>
                ) : (
                    [...submissionHistory].reverse().map((sub, i) => {
                        const v = VERDICTS[sub.verdict] || VERDICTS.queued;
                        const isSuccess = sub.verdict === 'accepted';
                        const isQueuedOrRunning = sub.verdict === 'queued' || sub.verdict === 'running';
                        const isError = !isSuccess && !isQueuedOrRunning;

                        const rowColor = isSuccess ? 'border-l-win bg-win/5 border-border' :
                                         isError ? 'border-l-loss bg-loss/5 border-border' :
                                         'border-l-border bg-bg-surface border-border';

                        const textColor = isSuccess ? 'text-win' : isError ? 'text-loss' : 'text-text-secondary';

                        return (
                            <div key={i} className={`flex items-center justify-between gap-2 px-2.5 sm:px-3 py-2 border-y border-r border-l-[3px] ${rowColor} transition-colors hover:brightness-110 font-mono text-xs min-w-0`}>
                                <div className="flex items-center gap-2 min-w-0">
                                    <span className={`${textColor} font-bold tracking-wide truncate`}>[{v.label.toUpperCase()}]</span>
                                </div>
                                <div className="flex items-center gap-2 sm:gap-4 text-text-muted opacity-90 shrink-0">
                                    {sub.runtime_ms != null && (
                                        <span className="hidden sm:inline">
                                            {sub.runtime_ms}ms
                                        </span>
                                    )}
                                    {sub.memory_kb != null && (
                                        <span className="hidden sm:inline">{Math.round(sub.memory_kb / 1024)}MB</span>
                                    )}
                                    {sub.passed != null && sub.total != null && (
                                        <span className={`px-1.5 py-0.5 rounded-sm whitespace-nowrap bg-bg-elevated ${textColor}`}>
                                            {isSuccess || isQueuedOrRunning
                                                ? `${sub.passed}/${sub.total}`
                                                : `FAIL @ ${sub.passed + 1}`
                                            }
                                        </span>
                                    )}
                                </div>
                            </div>
                        );
                    })
                )}
            </div>

            {opponentActivity && (
                <div className="absolute top-2 right-2 sm:right-4 z-50 max-w-[calc(100%-5rem)]">
                    <div className="flex items-center gap-2 bg-bg-elevated border border-border px-2 py-1 rounded-sm shadow-sm">
                        <Activity className="w-3 h-3 text-text-muted shrink-0" />
                        <span className="text-[10px] font-mono tracking-wide text-text-secondary truncate">
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
