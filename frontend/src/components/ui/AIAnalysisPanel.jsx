import { motion, AnimatePresence } from 'framer-motion';
import {
    Sparkles, Clock, AlertTriangle, CheckCircle2,
    Lightbulb, Code2, TrendingDown, X, ChevronRight
} from 'lucide-react';
import { useState } from 'react';

const ComplexityBadge = ({ label, value, variant = 'neutral' }) => {
    const colors = {
        good: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
        warn: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
        bad: 'bg-red-500/15 text-red-500 border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.15)]',
        neutral: 'bg-accent/10 text-accent border-accent/20',
    };
    return (
        <div className={`flex flex-col gap-1 px-4 py-3 rounded-xl border ${colors[variant]} transition-all duration-300 hover:scale-[1.02]`}>
            <span className="text-[10px] uppercase tracking-widest opacity-60 font-bold">{label}</span>
            <span className="font-mono text-lg font-bold">{value}</span>
        </div>
    );
};

const Section = ({ icon: Icon, title, children, defaultOpen = true, accent = false, glow = false }) => {
    const [open, setOpen] = useState(defaultOpen);
    
    // Aesthetic variants based on content importance
    const headerClass = accent 
        ? 'bg-gradient-to-r from-accent/10 via-accent/5 to-transparent border-b border-accent/10' 
        : glow
        ? 'bg-gradient-to-r from-win/10 via-transparent to-transparent border-b border-win/10'
        : 'bg-bg-surface/50 border-b border-border/50';

    return (
        <motion.div 
            layout
            className={`rounded-2xl border ${accent ? 'border-accent/20' : glow ? 'border-win/20' : 'border-border/60'} overflow-hidden bg-bg-surface/30 backdrop-blur-sm transition-all duration-300`}
            style={glow ? { boxShadow: '0 0 40px -10px rgba(16, 185, 129, 0.1)' } : {}}
        >
            <button
                onClick={() => setOpen(!open)}
                className={`w-full flex items-center justify-between px-5 py-4 ${headerClass} hover:brightness-110 transition-all`}
            >
                <div className="flex items-center gap-3">
                    <div className={`p-1.5 rounded-lg ${accent ? 'bg-accent/20 text-accent' : glow ? 'bg-win/20 text-win' : 'bg-bg-hover text-text-secondary'}`}>
                        <Icon size={16} />
                    </div>
                    <span className="text-sm font-bold uppercase tracking-widest text-text-primary">{title}</span>
                </div>
                <motion.div animate={{ rotate: open ? 90 : 0 }} transition={{ duration: 0.2 }}>
                    <ChevronRight size={16} className={accent ? 'text-accent/50' : 'text-text-muted'} />
                </motion.div>
            </button>
            <AnimatePresence initial={false}>
                {open && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: 'easeInOut' }}
                        className="overflow-hidden"
                    >
                        <div className="p-5">{children}</div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

const getComplexityVariant = (complexity) => {
    if (!complexity || complexity === 'N/A') return 'neutral';
    const s = complexity.toUpperCase();
    if (s.includes('O(1)') || s.includes('O(LOG') || s.includes('O(N LOG')) return 'good';
    if (s.includes('O(N²)') || s.includes('O(N^2)') || s.includes('O(2^N)') || s.includes('O(N!)')) return 'bad';
    return 'warn';
};

export default function AIAnalysisPanel({ analysis, verdict, onClose }) {
    const isAccepted = verdict?.status === 'accepted';

    if (!analysis) return null;

    return (
        <motion.div
            initial={{ opacity: 0, backdropFilter: 'blur(0px)' }}
            animate={{ opacity: 1, backdropFilter: 'blur(10px)' }}
            exit={{ opacity: 0, backdropFilter: 'blur(0px)' }}
            transition={{ duration: 0.4 }}
            className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-8"
            style={{ background: 'rgba(5, 7, 10, 0.85)' }}
        >
            <motion.div
                initial={{ scale: 0.95, y: 20 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.95, y: 20 }}
                transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                className="w-full max-w-5xl w-[95vw] h-[85vh] flex flex-col rounded-3xl bg-bg-primary border border-white/10 shadow-[0_0_80px_rgba(0,0,0,0.8)] overflow-hidden relative"
            >
                {/* Decorative top glow */}
                <div className="absolute top-0 left-1/4 right-1/4 h-[1px] bg-gradient-to-r from-transparent via-accent to-transparent opacity-50 blur-[2px]" />

                {/* Header */}
                <div className="flex items-center justify-between px-8 py-6 border-b border-white/5 shrink-0 bg-bg-surface/50">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent/30 to-accent/5 flex items-center justify-center border border-accent/20 shadow-[0_0_20px_rgba(102,126,234,0.2)]">
                            <Sparkles size={24} className="text-accent drop-shadow-[0_0_8px_rgba(102,126,234,0.8)]" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">Extensive Code Analysis</h2>
                            <p className="text-xs font-medium text-accent/80 tracking-wide uppercase mt-1">Intelligence Powered by Gemini 2.0</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-xl hover:bg-white/5 text-text-muted hover:text-white transition-all duration-200 hover:rotate-90"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Scrollable Content Body */}
                <div className="flex-1 overflow-y-auto p-6 lg:p-10 custom-scrollbar bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-bg-surface/20 via-bg-primary to-bg-root">
                    <div className="max-w-4xl mx-auto space-y-6">

                        {/* Top Banner Verification status */}
                        <div className={`rounded-2xl p-5 border shadow-lg ${isAccepted ? 'bg-gradient-to-r from-emerald-500/10 to-transparent border-emerald-500/20 shadow-emerald-500/5' : 'bg-gradient-to-r from-red-500/10 to-transparent border-red-500/20 shadow-red-500/5'}`}>
                            <div className="flex items-start gap-4">
                                <div className={`p-2 rounded-full ${isAccepted ? 'bg-emerald-500/20' : 'bg-red-500/20'} shrink-0`}>
                                    {isAccepted
                                        ? <CheckCircle2 size={24} className="text-emerald-400" />
                                        : <AlertTriangle size={24} className="text-red-400" />
                                    }
                                </div>
                                <div className="mt-0.5">
                                    <h3 className={`text-sm font-bold uppercase tracking-widest mb-1 ${isAccepted ? 'text-emerald-400' : 'text-red-400'}`}>
                                        Verdict Breakdown
                                    </h3>
                                    <p className="text-base text-text-primary leading-relaxed">
                                        {analysis.verdict_explanation}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Complexity Metrics Grid layout */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Original Complexity */}
                            <Section icon={Clock} title="Current Submission Metrics">
                                <div className="grid grid-cols-2 gap-4">
                                    <ComplexityBadge
                                        label="Time Complexity"
                                        value={analysis.time_complexity || 'N/A'}
                                        variant={getComplexityVariant(analysis.time_complexity)}
                                    />
                                    <ComplexityBadge
                                        label="Space Usage"
                                        value={analysis.space_complexity || 'N/A'}
                                        variant={getComplexityVariant(analysis.space_complexity)}
                                    />
                                </div>
                            </Section>

                            {/* Ideal target complexity */}
                            <Section icon={TrendingDown} title="Target Benchmarks" glow>
                                <div className="grid grid-cols-2 gap-4">
                                    <ComplexityBadge
                                        label="Optimized Time"
                                        value={analysis.optimized_time_complexity || 'N/A'}
                                        variant={getComplexityVariant(analysis.optimized_time_complexity)}
                                    />
                                    <ComplexityBadge
                                        label="Optimized Space"
                                        value={analysis.optimized_space_complexity || 'N/A'}
                                        variant={getComplexityVariant(analysis.optimized_space_complexity)}
                                    />
                                </div>
                            </Section>
                        </div>

                        {/* Issues section */}
                        {analysis.issues && analysis.issues.length > 0 && (
                            <Section icon={AlertTriangle} title="Identified Issues & Anti-patterns">
                                <div className="grid grid-cols-1 gap-3">
                                    {analysis.issues.map((issue, i) => (
                                        <div key={i} className="flex gap-4 p-4 rounded-xl bg-red-500/5 border border-red-500/10 items-start">
                                            <div className="w-6 h-6 rounded-full bg-red-500/10 flex items-center justify-center shrink-0 text-red-400 text-xs font-bold">{i+1}</div>
                                            <p className="text-sm text-text-primary leading-relaxed pt-0.5">{issue}</p>
                                        </div>
                                    ))}
                                </div>
                            </Section>
                        )}

                        {/* Specific Failing details scenario */}
                        {analysis.failed_test_explanation && (
                            <Section icon={AlertTriangle} title="Traceback: Why It Failed">
                                <div className="p-4 rounded-xl bg-bg-hover/30 border border-border/80 text-sm text-text-primary leading-relaxed">
                                    {analysis.failed_test_explanation}
                                </div>
                            </Section>
                        )}

                        {/* Highly Detailed Strategy Explanation */}
                        <Section icon={Lightbulb} title="Master Strategy & Algorithm Logic" accent>
                            <div className="prose prose-invert max-w-none text-sm leading-8 text-text-secondary">
                                {analysis.optimized_approach.split('\n').map((para, i) => (
                                    <p key={i} className={para.trim().length === 0 ? 'hidden' : 'mb-4'}>{para}</p>
                                ))}
                            </div>
                        </Section>

                        {/* Improved Code Reference block */}
                        {analysis.improved_code && (
                            <Section icon={Code2} title="Optimal Implementation Reference" defaultOpen={false}>
                                <div className="rounded-xl overflow-hidden border border-white/10 shadow-2xl relative group">
                                    {/* Mac-like header bar */}
                                    <div className="flex items-center gap-2 px-4 py-3 bg-[#1e1e1e] border-b border-white/5">
                                        <div className="w-3 h-3 rounded-full bg-red-500/80" />
                                        <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                                        <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                                        <div className="pl-2 flex-1">
                                            <span className="text-[10px] font-mono text-white/40 uppercase tracking-widest">solution.optimal</span>
                                        </div>
                                    </div>
                                    <pre className="m-0 p-5 pt-4 bg-[#141414] text-[13px] font-mono leading-relaxed text-[#d4d4d4] overflow-x-auto custom-scrollbar">
                                        <code>{analysis.improved_code}</code>
                                    </pre>
                                </div>
                            </Section>
                        )}

                        {/* Actionable Insights */}
                        {analysis.tips && analysis.tips.length > 0 && (
                            <Section icon={Sparkles} title="Actionable Learnings">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {analysis.tips.map((tip, i) => (
                                        <div key={i} className="flex gap-4 p-4 rounded-xl bg-bg-hover/50 border border-white/5 items-start hover:border-accent/40 transition-colors cursor-default hover:bg-accent/5">
                                            <span className="text-xl">✨</span>
                                            <p className="text-sm text-text-primary leading-snug pt-0.5">{tip}</p>
                                        </div>
                                    ))}
                                </div>
                            </Section>
                        )}

                        {/* Space at the bottom */}
                        <div className="h-4" />
                    </div>
                </div>

                {/* Fixed Footer Bar */}
                <div className="px-8 py-5 border-t border-white/10 shrink-0 flex items-center justify-between bg-bg-surface backdrop-blur-md">
                    <p className="text-xs font-medium text-text-muted">
                        Analysis helps you grow. Don't just copy—understand! 🚀
                    </p>
                    <button
                        onClick={onClose}
                        className="px-8 py-2.5 rounded-xl bg-gradient-to-r from-accent to-accent/80 text-white text-sm font-bold shadow-[0_4px_15px_rgba(102,126,234,0.4)] hover:shadow-[0_6px_25px_rgba(102,126,234,0.6)] hover:-translate-y-0.5 transition-all outline-none"
                    >
                        Back to Editor
                    </button>
                </div>
            </motion.div>
        </motion.div>
    );
}
