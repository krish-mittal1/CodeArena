import { motion, AnimatePresence } from 'framer-motion';
import {
    Sparkles, Clock, AlertTriangle, CheckCircle2,
    Lightbulb, Code2, X, ChevronRight, Target, ListChecks, Share2
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

const asList = (value) => {
    if (!value) return [];
    if (Array.isArray(value)) return value.map((v) => String(v).trim()).filter(Boolean);
    const text = String(value).trim();
    return text ? [text] : [];
};

const hasText = (value) => {
    const text = String(value || '').trim().toLowerCase();
    return !!text && text !== 'n/a' && text !== 'not available yet.';
};

/** Normalize new + legacy analysis payloads into one view model. */
const normalizeAnalysis = (analysis) => {
    if (!analysis || typeof analysis !== 'object') return null;

    const verdictSummary =
        analysis.verdict_summary
        || analysis.verdict_explanation
        || '';

    const rootCause =
        analysis.root_cause
        || asList(analysis.issues)[0]
        || analysis.failed_test_explanation
        || '';

    const keyInsight =
        analysis.key_insight
        || analysis.optimized_approach
        || analysis.problem_concept
        || '';

    let fixHints = asList(analysis.fix_hints);
    if (!fixHints.length && hasText(analysis.optimized_approach)) {
        fixHints = String(analysis.optimized_approach)
            .split(/\n+/)
            .map((p) => p.trim())
            .filter(Boolean)
            .slice(0, 5);
    }
    if (!fixHints.length) {
        fixHints = asList(analysis.tips).slice(0, 3);
    }

    return {
        verdictSummary,
        rootCause,
        timeComplexity: analysis.time_complexity || 'N/A',
        spaceComplexity: analysis.space_complexity || 'N/A',
        optimalTimeComplexity: analysis.optimal_time_complexity || analysis.optimized_time_complexity || 'N/A',
        optimalSpaceComplexity: analysis.optimal_space_complexity || analysis.optimized_space_complexity || 'N/A',
        keyInsight,
        fixHints,
        edgeCases: asList(analysis.edge_cases),
        improvedCode: analysis.improved_code || '',
        tips: asList(analysis.tips),
        failedTest: analysis.failed_test_explanation || '',
        issues: asList(analysis.issues),
    };
};

const resolveVerdictStatus = (verdict) => {
    if (!verdict) return '';
    if (typeof verdict === 'string') return verdict;
    return verdict.status || '';
};

const ComplexityPill = ({ label, value, highlight = false }) => (
    <div className={`flex flex-col gap-0.5 min-w-0 rounded-lg border px-3 py-2.5 ${highlight ? 'border-accent/30 bg-accent/5' : 'border-border bg-bg-surface'}`}>
        <span className="text-[10px] font-semibold uppercase tracking-wider text-text-muted">{label}</span>
        <span className={`font-mono text-sm font-semibold truncate ${highlight ? 'text-accent' : 'text-text-primary'}`}>{value || 'N/A'}</span>
    </div>
);

const Section = ({ icon: Icon, title, children, defaultOpen = true }) => {
    const [open, setOpen] = useState(defaultOpen);

    return (
        <div className="rounded-xl border border-border bg-bg-surface/60 overflow-hidden">
            <button
                type="button"
                onClick={() => setOpen(!open)}
                className="w-full flex items-center justify-between gap-3 px-4 py-3 text-left hover:bg-bg-hover/40 transition-colors"
            >
                <div className="flex items-center gap-2.5 min-w-0">
                    <Icon size={15} className="shrink-0 text-accent" />
                    <span className="text-sm font-semibold text-text-primary truncate">{title}</span>
                </div>
                <motion.span animate={{ rotate: open ? 90 : 0 }} transition={{ duration: 0.15 }} className="shrink-0 text-text-muted">
                    <ChevronRight size={16} />
                </motion.span>
            </button>
            <AnimatePresence initial={false}>
                {open && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                    >
                        <div className="px-4 pb-4 pt-1 border-t border-border/60">
                            {children}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

const StepList = ({ items, tone = 'neutral' }) => {
    const toneClass = tone === 'warn'
        ? 'bg-loss/10 text-loss border-loss/20'
        : tone === 'accent'
            ? 'bg-accent/10 text-accent border-accent/20'
            : 'bg-bg-hover text-text-secondary border-border';

    return (
        <ol className="space-y-2.5">
            {items.map((item, i) => (
                <li key={`${i}-${item.slice(0, 24)}`} className="flex gap-3">
                    <span className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-[11px] font-bold ${toneClass}`}>
                        {i + 1}
                    </span>
                    <p className="text-sm leading-6 text-text-primary pt-0.5">{item}</p>
                </li>
            ))}
        </ol>
    );
};

export default function AIAnalysisPanel({ analysis, verdict, onClose, shareSlug, onShare }) {
    const view = useMemo(() => normalizeAnalysis(analysis), [analysis]);
    const status = resolveVerdictStatus(verdict);
    const isAccepted = String(status).toLowerCase() === 'accepted' || String(status).toLowerCase() === 'ac';

    useEffect(() => {
        if (!onClose) return undefined;
        const onKey = (e) => {
            if (e.key === 'Escape') onClose();
        };
        window.addEventListener('keydown', onKey);
        return () => window.removeEventListener('keydown', onKey);
    }, [onClose]);

    if (!view) return null;

    const showRootCause = hasText(view.rootCause) && !isAccepted;
    const showFailedTest = hasText(view.failedTest);
    const showIssues = !showRootCause && view.issues.length > 0 && !isAccepted;

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-[500] flex items-end sm:items-center justify-center p-0 sm:p-4"
            style={{ background: 'rgba(0, 0, 0, 0.72)' }}
            role="dialog"
            aria-modal="true"
            aria-labelledby="ai-review-title"
            onClick={onClose || undefined}
        >
            <motion.div
                initial={{ y: 24, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: 24, opacity: 0 }}
                transition={{ type: 'spring', damping: 28, stiffness: 260 }}
                className="relative flex h-[min(94dvh,880px)] w-full sm:w-[min(96vw,720px)] flex-col overflow-hidden rounded-t-2xl sm:rounded-2xl border border-border bg-bg-primary shadow-2xl"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-start justify-between gap-3 border-b border-border bg-bg-surface px-4 sm:px-5 py-4 shrink-0">
                    <div className="flex items-start gap-3 min-w-0">
                        <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-border bg-bg-elevated text-accent">
                            <Sparkles size={18} />
                        </div>
                        <div className="min-w-0">
                            <h2 id="ai-review-title" className="text-base sm:text-lg font-bold text-text-primary truncate">
                                AI Code Review
                            </h2>
                            <p className="text-xs text-text-muted mt-0.5">
                                Structured coaching for this submission
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0">
                        {onShare && shareSlug && (
                            <button
                                type="button"
                                onClick={onShare}
                                className="flex items-center gap-1.5 rounded-lg px-2.5 py-2 text-xs font-medium text-text-secondary border border-border hover:bg-bg-hover"
                            >
                                <Share2 size={14} />
                                <span className="hidden sm:inline">Share</span>
                            </button>
                        )}
                        {onClose && (
                            <button
                                type="button"
                                onClick={onClose}
                                className="rounded-lg p-2 text-text-muted hover:bg-bg-hover hover:text-text-primary transition-colors"
                                aria-label="Close"
                            >
                                <X size={18} />
                            </button>
                        )}
                    </div>
                </div>

                {/* Body */}
                <div className="custom-scrollbar flex-1 overflow-y-auto px-4 sm:px-5 py-4 space-y-4">
                    {/* Verdict */}
                    <div className={`rounded-xl border p-4 ${isAccepted ? 'border-win/30 bg-win/8' : 'border-loss/30 bg-loss/8'}`}>
                        <div className="flex items-start gap-3">
                            <div className={`mt-0.5 shrink-0 ${isAccepted ? 'text-win' : 'text-loss'}`}>
                                {isAccepted ? <CheckCircle2 size={20} /> : <AlertTriangle size={20} />}
                            </div>
                            <div className="min-w-0 space-y-1">
                                <p className={`text-[11px] font-bold uppercase tracking-wider ${isAccepted ? 'text-win' : 'text-loss'}`}>
                                    {isAccepted ? 'Accepted' : 'Needs work'}
                                </p>
                                <p className="text-sm sm:text-[15px] leading-6 text-text-primary">
                                    {hasText(view.verdictSummary)
                                        ? view.verdictSummary
                                        : (isAccepted ? 'Your solution is correct.' : 'This submission needs a fix.')}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Complexity Comparison */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                        <ComplexityPill label="Your time" value={view.timeComplexity} />
                        <ComplexityPill label="Optimal time" value={view.optimalTimeComplexity} highlight />
                        <ComplexityPill label="Your space" value={view.spaceComplexity} />
                        <ComplexityPill label="Optimal space" value={view.optimalSpaceComplexity} highlight />
                    </div>

                    {/* Root cause */}
                    {(showRootCause || showIssues) && (
                        <Section icon={AlertTriangle} title="What's wrong">
                            {showRootCause ? (
                                <p className="text-sm leading-6 text-text-primary">{view.rootCause}</p>
                            ) : (
                                <StepList items={view.issues} tone="warn" />
                            )}
                            {showFailedTest && (
                                <div className="mt-3 rounded-lg border border-border bg-bg-hover/40 px-3 py-2.5">
                                    <p className="text-[10px] font-bold uppercase tracking-wider text-text-muted mb-1">
                                        Failed test
                                    </p>
                                    <p className="text-sm leading-6 text-text-secondary whitespace-pre-wrap">
                                        {view.failedTest}
                                    </p>
                                </div>
                            )}
                        </Section>
                    )}

                    {/* Key insight */}
                    {hasText(view.keyInsight) && (
                        <Section icon={Target} title="Key insight">
                            <p className="text-sm leading-6 text-text-primary whitespace-pre-wrap">
                                {view.keyInsight}
                            </p>
                        </Section>
                    )}

                    {/* Fix hints */}
                    {view.fixHints.length > 0 && (
                        <Section icon={Lightbulb} title={isAccepted ? 'How it works' : 'Fix hints'}>
                            <StepList items={view.fixHints} tone="accent" />
                        </Section>
                    )}

                    {/* Edge cases */}
                    {view.edgeCases.length > 0 && (
                        <Section icon={ListChecks} title="Edge cases to watch" defaultOpen={!isAccepted}>
                            <ul className="space-y-2">
                                {view.edgeCases.map((edge, i) => (
                                    <li
                                        key={`${i}-${edge.slice(0, 20)}`}
                                        className="flex gap-2.5 text-sm leading-6 text-text-primary"
                                    >
                                        <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-draw" />
                                        <span>{edge}</span>
                                    </li>
                                ))}
                            </ul>
                        </Section>
                    )}

                    {/* Improved code */}
                    {hasText(view.improvedCode) && (
                        <Section icon={Code2} title="Reference code" defaultOpen={false}>
                            <div className="overflow-hidden rounded-lg border border-border">
                                <div className="flex items-center gap-2 border-b border-border bg-bg-elevated px-3 py-2">
                                    <Clock size={12} className="text-text-muted" />
                                    <span className="font-mono text-[10px] uppercase tracking-wider text-text-muted">
                                        Compare structure — don&apos;t copy blindly
                                    </span>
                                </div>
                                <pre className="custom-scrollbar m-0 overflow-x-auto bg-bg-root p-3 sm:p-4 font-mono text-[12px] sm:text-[13px] leading-relaxed text-text-secondary">
                                    <code>{view.improvedCode}</code>
                                </pre>
                            </div>
                        </Section>
                    )}

                    {/* Tips */}
                    {view.tips.length > 0 && (
                        <Section icon={Sparkles} title="Remember next time" defaultOpen={false}>
                            <ul className="space-y-2">
                                {view.tips.map((tip, i) => (
                                    <li
                                        key={`${i}-${tip.slice(0, 20)}`}
                                        className="rounded-lg border border-border bg-bg-hover/30 px-3 py-2.5 text-sm leading-6 text-text-primary"
                                    >
                                        {tip}
                                    </li>
                                ))}
                            </ul>
                        </Section>
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between gap-3 border-t border-border bg-bg-surface px-4 sm:px-5 py-3.5 shrink-0">
                    <p className="hidden sm:block text-xs text-text-muted truncate">
                        Hints first — full spoilers only when useful.
                    </p>
                    {onClose ? (
                        <button
                            type="button"
                            onClick={onClose}
                            className="ml-auto rounded-lg bg-accent px-5 py-2.5 text-sm font-semibold text-white hover:bg-accent-hover transition-colors"
                        >
                            Back to Editor
                        </button>
                    ) : (
                        <span className="ml-auto text-xs text-text-muted">Insight library</span>
                    )}
                </div>
            </motion.div>
        </motion.div>
    );
}
