import { useBattleStore } from '../../stores/battleStore';
import { FileText, Clock, HardDrive, AlertCircle } from 'lucide-react';

export default function ProblemPanel() {
    const problem = useBattleStore((s) => s.problem);

    if (!problem) {
        return (
            <div className="flex items-center justify-center h-full bg-bg-root text-text-secondary">
                <div className="flex flex-col items-center gap-3">
                    <FileText className="w-6 h-6 opacity-30" />
                    <span className="text-xs font-medium tracking-wide">Fetching constraints...</span>
                </div>
            </div>
        );
    }

    const difficultyStyles = {
        easy: 'text-win border-win/30',
        medium: 'text-draw border-draw/30',
        hard: 'text-loss border-loss/30',
    };

    const diffLevel = problem.difficulty?.toLowerCase() || 'medium';
    const activeDifficultyColor = difficultyStyles[diffLevel] || difficultyStyles.medium;

    return (
        <div className="flex flex-col h-full bg-bg-root overflow-hidden text-text-primary">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-bg-primary">
                <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-text-secondary" />
                    <span className="text-sm font-semibold text-text-primary tracking-wide">Description</span>
                </div>
                {problem.difficulty && (
                    <span className={`px-2 py-0.5 rounded-sm text-[10px] font-bold uppercase tracking-wider border ${activeDifficultyColor}`}>
                        {problem.difficulty}
                    </span>
                )}
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">

                {/* Title & Description */}
                <div className="space-y-3">
                    <h2 className="text-xl font-bold tracking-tight text-text-primary">
                        {problem.title}
                    </h2>
                    <div className="text-sm text-text-secondary leading-relaxed">
                        <p className="whitespace-pre-wrap">{problem.description}</p>
                    </div>
                </div>

                {/* Examples */}
                {problem.examples?.length > 0 && (
                    <div className="space-y-4 pt-4 border-t border-border">
                        <h3 className="text-sm font-semibold text-text-primary flex items-center gap-2">
                            Examples
                        </h3>
                        {problem.examples.map((ex, i) => (
                            <div key={i} className="flex flex-col gap-2">
                                <div>
                                    <div className="text-[10px] font-bold uppercase tracking-wider text-text-muted mb-1 ml-1">Example {i + 1} Input</div>
                                    <div className="bg-bg-surface border border-border rounded-sm p-3 font-mono text-xs text-text-primary whitespace-pre-wrap shrink-0 break-words">
                                        {ex.input}
                                    </div>
                                </div>
                                <div>
                                    <div className="text-[10px] font-bold uppercase tracking-wider text-text-muted mb-1 ml-1">Example {i + 1} Output</div>
                                    <div className="bg-bg-surface border border-border rounded-sm p-3 font-mono text-xs text-text-primary whitespace-pre-wrap shrink-0 break-words">
                                        {ex.output}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Constraints */}
                {(problem.time_limit_ms || problem.memory_limit_mb) && (
                    <div className="pt-4 border-t border-border">
                        <h3 className="text-sm font-semibold text-text-primary flex items-center gap-2 mb-3">
                            <AlertCircle className="w-4 h-4 text-text-secondary" />
                            Constraints
                        </h3>
                        <div className="flex flex-col gap-2">
                            {problem.time_limit_ms && (
                                <div className="flex items-center gap-2 px-3 py-2 rounded-sm bg-bg-surface border border-border">
                                    <Clock className="w-4 h-4 text-text-secondary" />
                                    <span className="text-xs font-medium text-text-secondary">Time Limit:</span>
                                    <span className="font-mono text-xs text-text-primary">
                                        {problem.time_limit_ms} ms
                                    </span>
                                </div>
                            )}
                            {problem.memory_limit_mb && (
                                <div className="flex items-center gap-2 px-3 py-2 rounded-sm bg-bg-surface border border-border">
                                    <HardDrive className="w-4 h-4 text-text-secondary" />
                                    <span className="text-xs font-medium text-text-secondary">Memory Limit:</span>
                                    <span className="font-mono text-xs text-text-primary">
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
