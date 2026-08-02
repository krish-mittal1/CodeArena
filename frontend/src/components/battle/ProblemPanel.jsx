import { useBattleStore } from '../../stores/battleStore';
import { FileText, Clock, HardDrive, AlertCircle, Check } from 'lucide-react';
import ExampleBlocks from '../dsa/ExampleBlocks';
import ProblemDescription from '../dsa/ProblemDescription';

export default function ProblemPanel() {
    const problem = useBattleStore((s) => s.problem);
    const problems = useBattleStore((s) => s.problems);
    const problemId = useBattleStore((s) => s.problemId);
    const solvedProblemIds = useBattleStore((s) => s.solvedProblemIds);
    const setActiveProblem = useBattleStore((s) => s.setActiveProblem);

    const difficultyStyles = {
        easy: 'text-win border-win/30',
        medium: 'text-draw border-draw/30',
        hard: 'text-loss border-loss/30',
    };

    const diffLevel = problem?.difficulty?.toLowerCase() || 'medium';
    const activeDifficultyColor = difficultyStyles[diffLevel] || difficultyStyles.medium;
    const showTabs = problems.length > 1;

    return (
        <div className="flex flex-col h-full bg-bg-root overflow-hidden text-text-primary">
            {showTabs && (
                <div className="flex shrink-0 border-b border-border bg-bg-primary overflow-x-auto scrollbar-thin">
                    {problems.map((p, i) => {
                        const id = String(p.id);
                        const active = id === String(problemId);
                        const solved = solvedProblemIds.includes(id);
                        return (
                            <button
                                key={id}
                                type="button"
                                onClick={() => setActiveProblem(id)}
                                className={`flex items-center gap-1.5 px-3 py-2.5 text-xs font-semibold whitespace-nowrap min-h-[40px] border-b-2 transition-colors ${
                                    active
                                        ? 'text-text-primary border-accent'
                                        : 'text-text-muted border-transparent hover:text-text-secondary'
                                }`}
                            >
                                {solved ? (
                                    <Check className="w-3.5 h-3.5 text-win shrink-0" />
                                ) : (
                                    <span className="text-text-muted font-mono">{i + 1}</span>
                                )}
                                <span className="max-w-[140px] truncate">{p.title}</span>
                            </button>
                        );
                    })}
                </div>
            )}

            <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-bg-primary">
                <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-text-secondary" />
                    <span className="text-sm font-semibold text-text-primary tracking-wide">Description</span>
                </div>
                {problem?.difficulty && (
                    <span className={`px-2 py-0.5 rounded-sm text-[10px] font-bold uppercase tracking-wider border ${activeDifficultyColor}`}>
                        {problem.difficulty}
                    </span>
                )}
            </div>

            {!problem ? (
                <div className="flex items-center justify-center flex-1 bg-bg-root text-text-secondary">
                    <div className="flex flex-col items-center gap-3">
                        <FileText className="w-6 h-6 opacity-30" />
                        <span className="text-xs font-medium tracking-wide">Fetching constraints...</span>
                    </div>
                </div>
            ) : (
                <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
                    <div className="space-y-4">
                        <h2 className="text-xl font-bold tracking-tight text-text-primary">
                            {problem.title}
                        </h2>
                        <ProblemDescription problem={problem} showIoFormats={false} />
                    </div>

                    <div className="pt-2 border-t border-border">
                        <ExampleBlocks problem={problem} />
                    </div>

                    {(problem.time_limit_ms || problem.memory_limit_mb) && (
                        <div className="pt-4 border-t border-border">
                            <h3 className="text-sm font-semibold text-text-primary flex items-center gap-2 mb-3">
                                <AlertCircle className="w-4 h-4 text-text-secondary" />
                                Limits
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
            )}
        </div>
    );
}
