import { useBattleStore } from '../../stores/battleStore';
import { FileText, Clock, HardDrive, AlertCircle } from 'lucide-react';

export default function ProblemPanel() {
    const problem = useBattleStore((s) => s.problem);

    if (!problem) {
        return (
            <div className="flex items-center justify-center h-full bg-[#0e0e11] text-zinc-500">
                <div className="flex flex-col items-center gap-3 animate-pulse">
                    <FileText className="w-8 h-8 opacity-50" />
                    <span className="text-sm font-medium tracking-wide">Fetching problem constraints...</span>
                </div>
            </div>
        );
    }

    const difficultyStyles = {
        easy: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
        medium: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
        hard: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    };

    const diffLevel = problem.difficulty?.toLowerCase() || 'medium';
    const activeDifficultyColor = difficultyStyles[diffLevel] || difficultyStyles.medium;

    return (
        <div className="flex flex-col h-full bg-[#0e0e11] overflow-hidden text-zinc-300">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800/80 bg-zinc-900/30">
                <div className="flex items-center gap-2 text-zinc-100">
                    <FileText className="w-5 h-5 text-indigo-400" />
                    <span className="font-semibold tracking-wide">Problem Description</span>
                </div>
                {problem.difficulty && (
                    <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${activeDifficultyColor}`}>
                        {problem.difficulty}
                    </span>
                )}
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto p-6 sm:p-8 space-y-8 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent">

                {/* Title & Description */}
                <div className="space-y-4">
                    <h2 className="text-3xl font-bold tracking-tight text-white mb-6">
                        {problem.title}
                    </h2>
                    <div className="prose prose-invert prose-zinc max-w-none text-zinc-300 leading-relaxed">
                        <p className="whitespace-pre-wrap">{problem.description}</p>
                    </div>
                </div>

                {/* Examples */}
                {problem.examples?.length > 0 && (
                    <div className="space-y-6 pt-4 border-t border-zinc-800/50">
                        <h3 className="text-lg font-semibold text-zinc-200 flex items-center gap-2">
                            Examples
                        </h3>
                        {problem.examples.map((ex, i) => (
                            <div key={i} className="flex flex-col gap-3">
                                <div>
                                    <div className="text-xs font-semibold uppercase tracking-wider text-zinc-500 mb-1.5 ml-1">Example {i + 1} Input</div>
                                    <div className="bg-[#18181b] border border-zinc-800 rounded-xl p-4 font-mono text-sm text-zinc-300 whitespace-pre-wrap shrink-0 break-words shadow-inner">
                                        {ex.input}
                                    </div>
                                </div>
                                <div>
                                    <div className="text-xs font-semibold uppercase tracking-wider text-zinc-500 mb-1.5 ml-1">Example {i + 1} Output</div>
                                    <div className="bg-[#18181b] border border-zinc-800 rounded-xl p-4 font-mono text-emerald-400 text-sm whitespace-pre-wrap shrink-0 break-words shadow-inner">
                                        {ex.output}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Constraints */}
                {(problem.time_limit_ms || problem.memory_limit_mb) && (
                    <div className="pt-4 border-t border-zinc-800/50">
                        <h3 className="text-lg font-semibold text-zinc-200 flex items-center gap-2 mb-4">
                            <AlertCircle className="w-5 h-5 text-indigo-400" />
                            Constraints & Limits
                        </h3>
                        <div className="flex flex-col gap-3">
                            {problem.time_limit_ms && (
                                <div className="flex items-center gap-2 px-4 py-3 rounded-lg bg-zinc-900/50 border border-zinc-800/80">
                                    <Clock className="w-5 h-5 text-amber-500" />
                                    <span className="text-sm font-medium text-zinc-300">Time Limit:</span>
                                    <span className="font-mono text-sm text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded">
                                        {problem.time_limit_ms} ms
                                    </span>
                                </div>
                            )}
                            {problem.memory_limit_mb && (
                                <div className="flex items-center gap-2 px-4 py-3 rounded-lg bg-zinc-900/50 border border-zinc-800/80">
                                    <HardDrive className="w-5 h-5 text-indigo-500" />
                                    <span className="text-sm font-medium text-zinc-300">Memory Limit:</span>
                                    <span className="font-mono text-sm text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">
                                        {problem.memory_limit_mb} MB
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
