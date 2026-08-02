import {
    buildProblemExamples,
    formatDsaInput,
    formatDsaOutput,
} from '../../utils/dsaFormat';

function IoBlock({ label, children }) {
    return (
        <div className="min-w-0">
            <p className="text-[11px] font-semibold text-text-muted mb-1.5 tracking-wide">
                <span className="text-text-secondary">{label}:</span>
            </p>
            <pre className="px-3 py-2.5 text-[13px] sm:text-sm text-text-primary font-mono whitespace-pre-wrap break-words leading-relaxed bg-bg-root/80 border border-border/80 rounded-[4px] overflow-x-auto">
                {children}
            </pre>
        </div>
    );
}

/**
 * LeetCode-style Example 1 / Input / Output / Explanation blocks.
 */
export default function ExampleBlocks({ problem, className = '' }) {
    const examples = buildProblemExamples(problem);
    if (!examples.length) return null;

    const parameters = problem?.parameters || [];
    const returnType = problem?.return_type;

    return (
        <div className={`space-y-5 ${className}`}>
            <h3 className="text-sm font-semibold text-text-primary">Examples</h3>
            {examples.map((ex, i) => (
                <div
                    key={ex.key}
                    className="space-y-3 pb-5 border-b border-border last:border-b-0 last:pb-0"
                >
                    <p className="text-sm font-semibold text-text-primary">
                        Example {i + 1}:
                    </p>
                    <IoBlock label="Input">
                        {formatDsaInput(ex.input, parameters)}
                    </IoBlock>
                    <IoBlock label="Output">
                        {formatDsaOutput(ex.output, returnType)}
                    </IoBlock>
                    {ex.explanation && (
                        <div className="min-w-0">
                            <p className="text-[11px] font-semibold text-text-muted mb-1.5 tracking-wide">
                                <span className="text-text-secondary">Explanation:</span>
                            </p>
                            <p className="text-sm text-text-secondary leading-relaxed whitespace-pre-wrap">
                                {ex.explanation}
                            </p>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}

/**
 * Per-case run result: Input / Expected / Yours
 */
export function RunCaseBlocks({ cases, problem, className = '' }) {
    if (!cases?.length) return null;
    const parameters = problem?.parameters || [];
    const returnType = problem?.return_type;

    return (
        <div className={`space-y-3 ${className}`}>
            {cases.map((tc, idx) => {
                const passed = tc.verdict === 'accepted' || tc.passed === true;
                return (
                    <div
                        key={`${tc.order_index ?? idx}-${idx}`}
                        className={`p-3 border rounded-[6px] space-y-2.5 ${
                            passed
                                ? 'border-win/30 bg-win/5'
                                : 'border-border bg-bg-root'
                        }`}
                    >
                        <div className="flex items-center justify-between gap-2">
                            <p className="text-sm font-semibold text-text-primary">
                                Case {idx + 1}
                            </p>
                            <span
                                className={`text-xs font-semibold ${
                                    passed ? 'text-win' : 'text-loss'
                                }`}
                            >
                                {passed ? 'Accepted' : (tc.verdict || 'Wrong Answer')}
                            </span>
                        </div>
                        <IoBlock label="Input">
                            {formatDsaInput(tc.input, parameters)}
                        </IoBlock>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                            <IoBlock label="Expected">
                                {formatDsaOutput(tc.expected_output, returnType)}
                            </IoBlock>
                            <IoBlock label="Yours">
                                {tc.error_output
                                    || formatDsaOutput(tc.actual_output, returnType)
                                    || 'No output'}
                            </IoBlock>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
