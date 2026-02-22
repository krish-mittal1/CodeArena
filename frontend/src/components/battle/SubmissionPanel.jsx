import { useBattleStore } from '../../stores/battleStore';
import { VERDICTS } from '../../utils/constants';
import { Activity, History, ServerCrash, CheckCircle2, XCircle, Clock } from 'lucide-react';

export default function SubmissionPanel() {
    const submissionHistory = useBattleStore((s) => s.submissionHistory);
    const submissionStatus = useBattleStore((s) => s.submissionStatus);
    const opponentActivity = useBattleStore((s) => s.opponentActivity);

    return (
        <div className="flex flex-col h-64 bg-slate-950 border-t border-slate-800 z-20 shrink-0">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-3 bg-slate-900 border-b border-slate-800 shrink-0">
                <div className="flex items-center gap-2">
                    {submissionStatus === 'running' || submissionStatus === 'submitting' ? (
                        <>
                            <div className="w-4 h-4 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
                            <span className="text-sm font-semibold text-indigo-400 tracking-wide">Evaluating...</span>
                        </>
                    ) : (
                        <>
                            <Activity className="w-4 h-4 text-slate-400" />
                            <span className="text-sm font-semibold text-white tracking-wide">Test Results</span>
                        </>
                    )}
                </div>
                <span className="text-xs font-mono tracking-widest text-slate-500 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                    {submissionHistory.length} ATTEMPTS
                </span>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
                {submissionHistory.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-slate-500 gap-2">
                        <span className="text-sm font-medium">No active submissions</span>
                    </div>
                ) : (
                    [...submissionHistory].reverse().map((sub, i) => {
                        const v = VERDICTS[sub.verdict] || VERDICTS.queued;
                        // Map old verdict styles to new tailwind colors if they aren't pre-mapped
                        const colorMap = {
                            "text-green-500": "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
                            "text-red-500": "text-rose-400 bg-rose-500/10 border-rose-500/20",
                            "text-yellow-500": "text-amber-400 bg-amber-500/10 border-amber-500/20",
                        };
                        const bgColor = colorMap[v.color] || "text-slate-300 bg-slate-900 border-slate-800";

                        return (
                            <div key={i} className={`flex items-center justify-between p-3 rounded-lg border ${bgColor} shadow-sm transition-all hover:brightness-110`}>
                                <div className="flex items-center gap-2.5">
                                    <span className="text-lg">{v.icon}</span>
                                    <span className="font-bold text-sm tracking-wide">{v.label}</span>
                                </div>
                                <div className="flex items-center gap-4 text-xs font-mono opacity-80">
                                    {sub.time_ms != null && (
                                        <span className="flex items-center gap-1">
                                            <Clock className="w-3 h-3" /> {sub.time_ms}ms
                                        </span>
                                    )}
                                    {sub.memory_mb != null && (
                                        <span>{sub.memory_mb}MB</span>
                                    )}
                                    {sub.passed_count != null && sub.total_count != null && (
                                        <span className={`px-1.5 py-0.5 rounded font-semibold whitespace-nowrap ${sub.verdict === 'accepted' ? 'bg-black/20 text-emerald-400' : 'bg-black/20 text-rose-400'}`}>
                                            {sub.verdict === 'accepted' || sub.verdict === 'queued' || sub.verdict === 'running'
                                                ? `${sub.passed_count} / ${sub.total_count} passing`
                                                : `Failed on test ${sub.passed_count + 1}`
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
                <div className="absolute top-3 right-4 transform z-50 animate-in fade-in slide-in-from-top-2 duration-300">
                    <div className="flex items-center gap-2 bg-indigo-900/40 backdrop-blur-md border border-indigo-500/30 text-indigo-200 px-3 py-1.5 rounded-full shadow-lg">
                        <Activity className="w-4 h-4 text-indigo-400 animate-pulse" />
                        <span className="text-xs font-semibold tracking-wide">
                            Opponent Action:
                            <span className="ml-1 text-white opacity-90">
                                {opponentActivity.verdict ? (VERDICTS[opponentActivity.verdict]?.label || opponentActivity.verdict) : 'Submitted'}
                            </span>
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
}
