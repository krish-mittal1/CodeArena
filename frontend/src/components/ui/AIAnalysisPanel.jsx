import { motion, AnimatePresence } from 'framer-motion';
import {
    Sparkles, Clock, Database, AlertTriangle, CheckCircle2,
    Lightbulb, Code2, TrendingDown, ChevronDown, ChevronUp, X
} from 'lucide-react';
import { useState } from 'react';

const ComplexityBadge = ({ label, value, variant = 'neutral' }) => {
    const colors = {
        good: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
        warn: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
        bad: 'bg-red-500/15 text-red-400 border-red-500/30',
        neutral: 'bg-accent/10 text-accent border-accent/20',
    };
    return (
        <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${colors[variant]} text-xs font-mono`}>
            <span className="text-[10px] uppercase tracking-wider opacity-70 font-sans">{label}</span>
            <span className="font-bold text-sm">{value}</span>
        </div>
    );
};

const Section = ({ icon: Icon, title, children, defaultOpen = true, accent = false }) => {
    const [open, setOpen] = useState(defaultOpen);
    return (
        <div className={`rounded-xl border ${accent ? 'border-accent/30 bg-accent/5' : 'border-border bg-bg-surface'} overflow-hidden`}>
            <button
                onClick={() => setOpen(!open)}
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-bg-hover/50 transition-colors"
            >
                <div className="flex items-center gap-2.5">
                    <Icon size={15} className={accent ? 'text-accent' : 'text-text-secondary'} />
                    <span className="text-xs font-bold uppercase tracking-wider text-text-primary">{title}</span>
                </div>
                {open ? <ChevronUp size={14} className="text-text-muted" /> : <ChevronDown size={14} className="text-text-muted" />}
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
                        <div className="px-4 pb-4 pt-1">{children}</div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

const getComplexityVariant = (complexity) => {
    if (!complexity) return 'neutral';
    const s = complexity.toUpperCase();
    if (s.includes('O(1)') || s.includes('O(LOG') || s.includes('O(N LOG')) return 'good';
    if (s.includes('O(N²)') || s.includes('O(N^2)') || s.includes('O(2^N)') || s.includes('O(N!)')) return 'bad';
    return 'warn';
};

export default function AIAnalysisPanel({ analysis, verdict, onClose }) {
    const [showCode, setShowCode] = useState(false);
    const isAccepted = verdict?.status === 'accepted';

    if (!analysis) return null;

    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ type: 'spring', damping: 20, stiffness: 180 }}
            className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 sm:p-6"
            style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(6px)' }}
        >
            <motion.div
                initial={{ scale: 0.96 }}
                animate={{ scale: 1 }}
                className="w-full max-w-2xl max-h-[90vh] flex flex-col rounded-2xl bg-bg-primary border border-border shadow-2xl overflow-hidden"
            >
                {/* Header */}
                <div className="flex items-center justify-between px-5 py-4 border-b border-border shrink-0 bg-gradient-to-r from-accent/10 to-transparent">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center">
                            <Sparkles size={16} className="text-accent" />
                        </div>
                        <div>
                            <h2 className="text-sm font-bold text-text-primary">AI Code Analysis</h2>
                            <p className="text-[11px] text-text-muted">Powered by Google Gemini</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-1.5 rounded-lg hover:bg-bg-hover text-text-muted hover:text-text-primary transition-colors"
                    >
                        <X size={16} />
                    </button>
                </div>

                {/* Scrollable Content */}
                <div className="flex-1 overflow-y-auto p-5 space-y-4">

                    {/* Verdict Explanation */}
                    <div className={`rounded-xl p-4 border ${isAccepted ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-red-500/10 border-red-500/30'}`}>
                        <div className="flex items-start gap-3">
                            {isAccepted
                                ? <CheckCircle2 size={18} className="text-emerald-400 shrink-0 mt-0.5" />
                                : <AlertTriangle size={18} className="text-red-400 shrink-0 mt-0.5" />
                            }
                            <p className="text-sm text-text-secondary leading-relaxed">
                                {analysis.verdict_explanation}
                            </p>
                        </div>
                    </div>

                    {/* Complexity — Your Code */}
                    <Section icon={Clock} title="Your Code — Complexity">
                        <div className="flex flex-wrap gap-3 mt-2">
                            <ComplexityBadge
                                label="Time"
                                value={analysis.time_complexity || 'N/A'}
                                variant={getComplexityVariant(analysis.time_complexity)}
                            />
                            <ComplexityBadge
                                label="Space"
                                value={analysis.space_complexity || 'N/A'}
                                variant={getComplexityVariant(analysis.space_complexity)}
                            />
                        </div>
                    </Section>

                    {/* Issues (only shown if there are any) */}
                    {analysis.issues && analysis.issues.length > 0 && (
                        <Section icon={AlertTriangle} title="Issues Found">
                            <ul className="mt-2 space-y-2">
                                {analysis.issues.map((issue, i) => (
                                    <li key={i} className="flex items-start gap-2.5 text-sm text-text-secondary">
                                        <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-red-400 shrink-0" />
                                        {issue}
                                    </li>
                                ))}
                            </ul>
                        </Section>
                    )}

                    {/* Failed test case explanation */}
                    {analysis.failed_test_explanation && (
                        <Section icon={AlertTriangle} title="Why It Failed">
                            <p className="text-sm text-text-secondary leading-relaxed mt-1">
                                {analysis.failed_test_explanation}
                            </p>
                        </Section>
                    )}

                    {/* Optimized Approach */}
                    <Section icon={TrendingDown} title="Optimized Approach" accent defaultOpen>
                        <div className="space-y-3 mt-2">
                            <p className="text-sm text-text-secondary leading-relaxed">
                                {analysis.optimized_approach}
                            </p>
                            {(analysis.optimized_time_complexity || analysis.optimized_space_complexity) && (
                                <div className="flex flex-wrap gap-3 pt-2">
                                    {analysis.optimized_time_complexity && (
                                        <ComplexityBadge
                                            label="Optimized Time"
                                            value={analysis.optimized_time_complexity}
                                            variant={getComplexityVariant(analysis.optimized_time_complexity)}
                                        />
                                    )}
                                    {analysis.optimized_space_complexity && (
                                        <ComplexityBadge
                                            label="Optimized Space"
                                            value={analysis.optimized_space_complexity}
                                            variant={getComplexityVariant(analysis.optimized_space_complexity)}
                                        />
                                    )}
                                </div>
                            )}
                        </div>
                    </Section>

                    {/* Improved Code */}
                    {analysis.improved_code && (
                        <Section icon={Code2} title="Improved Code" defaultOpen={false}>
                            <div className="mt-2">
                                <button
                                    onClick={() => setShowCode(!showCode)}
                                    className="mb-3 text-xs text-accent hover:underline"
                                >
                                    {showCode ? 'Hide code' : 'Show improved code'}
                                </button>
                                <AnimatePresence>
                                    {showCode && (
                                        <motion.pre
                                            initial={{ opacity: 0, height: 0 }}
                                            animate={{ opacity: 1, height: 'auto' }}
                                            exit={{ opacity: 0, height: 0 }}
                                            className="bg-bg-root rounded-lg p-4 text-xs font-mono text-text-primary overflow-x-auto border border-border whitespace-pre-wrap"
                                        >
                                            {analysis.improved_code}
                                        </motion.pre>
                                    )}
                                </AnimatePresence>
                            </div>
                        </Section>
                    )}

                    {/* Tips */}
                    {analysis.tips && analysis.tips.length > 0 && (
                        <Section icon={Lightbulb} title="Tips to Improve">
                            <ul className="mt-2 space-y-2.5">
                                {analysis.tips.map((tip, i) => (
                                    <li key={i} className="flex items-start gap-2.5 text-sm text-text-secondary">
                                        <span className="text-amber-400 shrink-0 mt-0.5">💡</span>
                                        {tip}
                                    </li>
                                ))}
                            </ul>
                        </Section>
                    )}
                </div>

                {/* Footer */}
                <div className="px-5 py-3 border-t border-border shrink-0 flex justify-end bg-bg-surface/50">
                    <button
                        onClick={onClose}
                        className="px-5 py-2 rounded-lg bg-accent text-white text-xs font-bold hover:bg-accent/90 transition-colors"
                    >
                        Got it!
                    </button>
                </div>
            </motion.div>
        </motion.div>
    );
}
