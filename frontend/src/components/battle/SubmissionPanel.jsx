import { useBattleStore } from '../../stores/battleStore';
import { VERDICTS } from '../../utils/constants';
import { Activity, History, ServerCrash, CheckCircle2, XCircle, Clock } from 'lucide-react';

export default function SubmissionPanel() {
    const submissionHistory = useBattleStore((s) => s.submissionHistory);
    const submissionStatus = useBattleStore((s) => s.submissionStatus);
    const opponentActivity = useBattleStore((s) => s.opponentActivity);

    return (
        <div className="flex flex-col h-[280px] bg-[#121214] border-t border-zinc-800/80 z-20 shrink-0 shadow-[0_-4px_24px_rgba(0,0,0,0.5)]">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-2 bg-[#18181b] border-b border-zinc-800/80 shadow-sm shrink-0">
                <div className="flex items-center gap-2">
                    {submissionStatus === 'running' || submissionStatus === 'submitting' ? (
                        <>
                            <div className="w-4 h-4 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
                            <span className="text-sm font-semibold text-indigo-400 tracking-wide">Evaluating...</span>
                        </>
                    ) : (
                        <>
                            <History className="w-4 h-4 text-zinc-400" />
                            <span className="text-sm font-bold text-zinc-300 tracking-wide">Test Results</span>
                        </>
                    )}
                </div>
                <span className="text-xs font-semibold uppercase tracking-widest text-zinc-500 bg-zinc-800/50 px-2 py-0.5 rounded-md">
                    {submissionHistory.length} Attempts
                </span>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent">
                {submissionHistory.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-zinc-600 gap-2">
                        <ServerCrash className="w-8 h-8 opacity-20" />
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
                        const bgColor = colorMap[v.color] || "text-zinc-300 bg-zinc-800/50 border-zinc-700/50";

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
                                        <span className="bg-black/20 px-1.5 py-0.5 rounded font-semibold whitespace-nowrap">
                                            {sub.passed_count} / {sub.total_count} passing
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
