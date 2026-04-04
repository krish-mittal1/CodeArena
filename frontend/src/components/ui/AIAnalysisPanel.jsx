import { motion, AnimatePresence } from 'framer-motion';
import {
    Sparkles, Clock, AlertTriangle, CheckCircle2,
    Lightbulb, Code2, TrendingDown, X, ChevronRight, GitBranch, BookOpen
} from 'lucide-react';
import { useMemo, useState } from 'react';

const splitParagraphs = (text) =>
    String(text || '')
        .split(/\n+/)
        .map((part) => part.trim())
        .filter(Boolean);

const splitSentences = (text) =>
    String(text || '')
        .split(/(?<=[.!?])\s+/)
        .map((part) => part.trim())
        .filter(Boolean);

const pickMainIdea = (analysis) => {
    const sources = [
        analysis?.optimized_approach,
        analysis?.verdict_explanation,
        analysis?.tips?.[0],
    ];

    for (const source of sources) {
        const firstSentence = splitSentences(source)[0];
        if (firstSentence) return firstSentence;
    }

    return 'The AI review could not produce a short summary yet.';
};

const buildQuickSummary = (analysis, isAccepted) => {
    const mainIdea = pickMainIdea(analysis);
    const firstIssue = analysis?.issues?.[0];
    const firstTip = analysis?.tips?.[0];

    return [
        {
            label: isAccepted ? 'Result' : 'Main issue',
            value: isAccepted ? 'Your solution is correct.' : (firstIssue || 'The solution needs one more fix.'),
            tone: isAccepted ? 'good' : 'bad',
        },
        {
            label: 'Core idea',
            value: mainIdea,
            tone: 'neutral',
        },
        {
            label: 'Remember',
            value: firstTip || (isAccepted
                ? 'Keep this pattern in mind for similar problems.'
                : 'Focus on one improvement at a time and test edge cases early.'),
            tone: 'warn',
        },
    ];
};

const buildApproachSteps = (analysis) => {
    const paragraphs = splitParagraphs(analysis?.optimized_approach);
    if (paragraphs.length > 1) return paragraphs;

    const sentences = splitSentences(analysis?.optimized_approach);
    if (sentences.length <= 1) return sentences;

    return sentences.map((sentence, index) => `${index + 1}. ${sentence}`);
};

const normalizeAlternatives = (analysis) => {
    if (!Array.isArray(analysis?.alternative_approaches)) return [];

    return analysis.alternative_approaches
        .map((item, index) => {
            if (!item) return null;
            if (typeof item === 'string') {
                return {
                    name: `Alternative ${index + 1}`,
                    summary: item,
                    time_complexity: 'N/A',
                    space_complexity: 'N/A',
                    when_to_use: '',
                };
            }

            return {
                name: item.name || `Alternative ${index + 1}`,
                summary: item.summary || '',
                time_complexity: item.time_complexity || 'N/A',
                space_complexity: item.space_complexity || 'N/A',
                when_to_use: item.when_to_use || '',
            };
        })
        .filter(Boolean);
};

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

const SummaryCard = ({ label, value, tone = 'neutral' }) => {
    const tones = {
        good: 'border-emerald-500/20 bg-emerald-500/8',
        warn: 'border-amber-500/20 bg-amber-500/8',
        bad: 'border-red-500/20 bg-red-500/8',
        neutral: 'border-white/8 bg-white/[0.03]',
    };

    return (
        <div className={`rounded-2xl border p-4 ${tones[tone]}`}>
            <p className="text-[10px] font-bold uppercase tracking-[0.24em] text-text-muted mb-2">{label}</p>
            <p className="text-sm leading-7 text-text-primary">{value}</p>
        </div>
    );
};

const Section = ({ icon: Icon, title, subtitle, children, defaultOpen = true, accent = false, glow = false }) => {
    const [open, setOpen] = useState(defaultOpen);

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
                className={`w-full flex items-center justify-between px-5 py-4 text-left ${headerClass} hover:brightness-110 transition-all`}
            >
                <div className="flex items-center gap-3">
                    <div className={`p-1.5 rounded-lg ${accent ? 'bg-accent/20 text-accent' : glow ? 'bg-win/20 text-win' : 'bg-bg-hover text-text-secondary'}`}>
                        <Icon size={16} />
                    </div>
                    <div>
                        <span className="block text-sm font-bold uppercase tracking-widest text-text-primary">{title}</span>
                        {subtitle && (
                            <span className="block mt-1 text-xs text-text-muted normal-case tracking-normal font-medium">
                                {subtitle}
                            </span>
                        )}
                    </div>
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
    if (s.includes('O(N^2)') || s.includes('O(N²)') || s.includes('O(2^N)') || s.includes('O(N!)')) return 'bad';
    return 'warn';
};

const ApproachCard = ({ title, description, time, space, icon: Icon, tone = 'neutral' }) => {
    const tones = {
        neutral: 'border-white/8 bg-white/[0.03]',
        bad: 'border-red-500/20 bg-red-500/[0.05]',
        good: 'border-emerald-500/20 bg-emerald-500/[0.05]',
        accent: 'border-accent/20 bg-accent/[0.06]',
    };

    return (
        <div className={`rounded-2xl border p-5 ${tones[tone]}`}>
            <div className="flex items-start justify-between gap-4 mb-4">
                <div className="flex items-center gap-3">
                    <div className={`rounded-xl p-2 ${tone === 'good' ? 'bg-emerald-500/15 text-emerald-400' : tone === 'bad' ? 'bg-red-500/15 text-red-400' : tone === 'accent' ? 'bg-accent/15 text-accent' : 'bg-bg-hover text-text-secondary'}`}>
                        <Icon size={16} />
                    </div>
                    <div>
                        <h4 className="text-sm font-bold uppercase tracking-[0.18em] text-text-primary">{title}</h4>
                    </div>
                </div>
            </div>
            <p className="text-sm leading-7 text-text-primary mb-4 whitespace-pre-wrap">{description || 'Not available yet.'}</p>
            <div className="grid grid-cols-2 gap-3">
                <ComplexityBadge label="Time" value={time || 'N/A'} variant={getComplexityVariant(time)} />
                <ComplexityBadge label="Space" value={space || 'N/A'} variant={getComplexityVariant(space)} />
            </div>
        </div>
    );
};

export default function AIAnalysisPanel({ analysis, verdict, onClose }) {
    const isAccepted = verdict?.status === 'accepted';

    const quickSummary = useMemo(() => buildQuickSummary(analysis, isAccepted), [analysis, isAccepted]);
    const verdictParagraphs = useMemo(() => splitParagraphs(analysis?.verdict_explanation), [analysis?.verdict_explanation]);
    const approachSteps = useMemo(() => buildApproachSteps(analysis), [analysis]);
    const conceptParagraphs = useMemo(() => splitParagraphs(analysis?.problem_concept), [analysis?.problem_concept]);
    const currentApproachParagraphs = useMemo(() => splitParagraphs(analysis?.submitted_approach), [analysis?.submitted_approach]);
    const alternativeApproaches = useMemo(() => normalizeAlternatives(analysis), [analysis]);
    const learnings = useMemo(
        () => (analysis?.tips?.length ? analysis.tips : splitSentences(analysis?.optimized_approach).slice(0, 3)),
        [analysis?.optimized_approach, analysis?.tips]
    );

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
                className="relative flex h-[85vh] w-[95vw] max-w-5xl flex-col overflow-hidden rounded-3xl border border-white/10 bg-bg-primary shadow-[0_0_80px_rgba(0,0,0,0.8)]"
            >
                <div className="absolute left-1/4 right-1/4 top-0 h-[1px] bg-gradient-to-r from-transparent via-accent to-transparent opacity-50 blur-[2px]" />

                <div className="flex items-center justify-between border-b border-white/5 bg-bg-surface/50 px-8 py-6 shrink-0">
                    <div className="flex items-center gap-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-accent/20 bg-gradient-to-br from-accent/30 to-accent/5 shadow-[0_0_20px_rgba(102,126,234,0.2)]">
                            <Sparkles size={24} className="text-accent drop-shadow-[0_0_8px_rgba(102,126,234,0.8)]" />
                        </div>
                        <div>
                            <h2 className="bg-gradient-to-r from-white to-white/70 bg-clip-text text-xl font-bold text-transparent">
                                AI Code Review
                            </h2>
                            <p className="mt-1 text-xs font-medium uppercase tracking-wide text-accent/80">
                                Clear explanation of your submission
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="rounded-xl p-2 text-text-muted transition-all duration-200 hover:bg-white/5 hover:text-white hover:rotate-90"
                    >
                        <X size={20} />
                    </button>
                </div>

                <div className="custom-scrollbar flex-1 overflow-y-auto bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-bg-surface/20 via-bg-primary to-bg-root p-6 lg:p-10">
                    <div className="mx-auto max-w-4xl space-y-6">
                        <div className={`rounded-2xl border p-5 shadow-lg ${isAccepted ? 'border-emerald-500/20 bg-gradient-to-r from-emerald-500/10 to-transparent shadow-emerald-500/5' : 'border-red-500/20 bg-gradient-to-r from-red-500/10 to-transparent shadow-red-500/5'}`}>
                            <div className="flex items-start gap-4">
                                <div className={`shrink-0 rounded-full p-2 ${isAccepted ? 'bg-emerald-500/20' : 'bg-red-500/20'}`}>
                                    {isAccepted
                                        ? <CheckCircle2 size={24} className="text-emerald-400" />
                                        : <AlertTriangle size={24} className="text-red-400" />
                                    }
                                </div>
                                <div className="w-full">
                                    <h3 className={`mb-3 text-sm font-bold uppercase tracking-widest ${isAccepted ? 'text-emerald-400' : 'text-red-400'}`}>
                                        {isAccepted ? 'Why this solution works' : 'Why this submission failed'}
                                    </h3>
                                    <div className="grid gap-3 md:grid-cols-3">
                                        {quickSummary.map((item) => (
                                            <SummaryCard
                                                key={item.label}
                                                label={item.label}
                                                value={item.value}
                                                tone={item.tone}
                                            />
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <Section
                            icon={BookOpen}
                            title="Core concept of the problem"
                            subtitle="What the problem is really asking and what pattern usually solves it"
                            accent
                        >
                            <div className="space-y-3">
                                {conceptParagraphs.map((paragraph, index) => (
                                    <div
                                        key={`${paragraph}-${index}`}
                                        className="rounded-xl border border-white/6 bg-white/[0.03] px-4 py-3"
                                    >
                                        <p className="text-sm leading-7 text-text-primary">{paragraph}</p>
                                    </div>
                                ))}
                            </div>
                        </Section>

                        <Section
                            icon={Lightbulb}
                            title="Simple Explanation"
                            subtitle="A cleaner, easier-to-read breakdown of the AI verdict"
                            accent
                        >
                            <div className="space-y-3">
                                {verdictParagraphs.map((paragraph, index) => (
                                    <div
                                        key={`${paragraph}-${index}`}
                                        className="rounded-xl border border-white/6 bg-white/[0.03] px-4 py-3"
                                    >
                                        <p className="text-sm leading-7 text-text-primary">{paragraph}</p>
                                    </div>
                                ))}
                            </div>
                        </Section>

                        <Section
                            icon={GitBranch}
                            title="Approach ladder"
                            subtitle="Compare the slower idea, your current idea, and the strongest common solution"
                            accent
                        >
                            <div className="grid grid-cols-1 gap-4">
                                <ApproachCard
                                    title="Worst reasonable approach"
                                    description={analysis?.worst_approach}
                                    time={analysis?.worst_time_complexity}
                                    space={analysis?.worst_space_complexity}
                                    icon={TrendingDown}
                                    tone="bad"
                                />
                                <ApproachCard
                                    title="Your current approach"
                                    description={currentApproachParagraphs.join('\n\n')}
                                    time={analysis?.time_complexity}
                                    space={analysis?.space_complexity}
                                    icon={Code2}
                                    tone="neutral"
                                />
                                <ApproachCard
                                    title="Optimal approach"
                                    description={analysis?.optimized_approach}
                                    time={analysis?.optimized_time_complexity}
                                    space={analysis?.optimized_space_complexity}
                                    icon={Sparkles}
                                    tone="good"
                                />
                            </div>
                        </Section>

                        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                            <Section icon={Clock} title="Your Complexity" subtitle="What your current solution is using">
                                <div className="grid grid-cols-2 gap-4">
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

                            <Section icon={TrendingDown} title="Good Target" subtitle="What a strong solution usually aims for" glow>
                                <div className="grid grid-cols-2 gap-4">
                                    <ComplexityBadge
                                        label="Best Time"
                                        value={analysis.optimized_time_complexity || 'N/A'}
                                        variant={getComplexityVariant(analysis.optimized_time_complexity)}
                                    />
                                    <ComplexityBadge
                                        label="Best Space"
                                        value={analysis.optimized_space_complexity || 'N/A'}
                                        variant={getComplexityVariant(analysis.optimized_space_complexity)}
                                    />
                                </div>
                            </Section>
                        </div>

                        {alternativeApproaches.length > 0 && (
                            <Section
                                icon={GitBranch}
                                title="Other possible approaches"
                                subtitle="Useful alternatives so the user can compare trade-offs and patterns"
                            >
                                <div className="space-y-4">
                                    {alternativeApproaches.map((approach, index) => (
                                        <div key={`${approach.name}-${index}`} className="rounded-2xl border border-white/8 bg-white/[0.03] p-5">
                                            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                                                <div className="flex-1">
                                                    <p className="text-sm font-bold uppercase tracking-[0.18em] text-text-primary mb-3">
                                                        {approach.name}
                                                    </p>
                                                    <p className="text-sm leading-7 text-text-primary whitespace-pre-wrap">
                                                        {approach.summary}
                                                    </p>
                                                    {approach.when_to_use && (
                                                        <p className="mt-3 text-sm leading-7 text-text-secondary">
                                                            <span className="font-semibold text-text-primary">When to use:</span> {approach.when_to_use}
                                                        </p>
                                                    )}
                                                </div>
                                                <div className="grid grid-cols-2 gap-3 lg:w-[250px]">
                                                    <ComplexityBadge
                                                        label="Time"
                                                        value={approach.time_complexity}
                                                        variant={getComplexityVariant(approach.time_complexity)}
                                                    />
                                                    <ComplexityBadge
                                                        label="Space"
                                                        value={approach.space_complexity}
                                                        variant={getComplexityVariant(approach.space_complexity)}
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </Section>
                        )}

                        {analysis.issues && analysis.issues.length > 0 && (
                            <Section
                                icon={AlertTriangle}
                                title="What Needs Attention"
                                subtitle="These are the main things the AI thinks you should fix"
                            >
                                <div className="grid gap-3">
                                    {analysis.issues.map((issue, i) => (
                                        <div key={i} className="flex items-start gap-4 rounded-xl border border-red-500/10 bg-red-500/5 p-4">
                                            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-red-500/10 text-xs font-bold text-red-400">
                                                {i + 1}
                                            </div>
                                            <p className="pt-0.5 text-sm leading-7 text-text-primary">{issue}</p>
                                        </div>
                                    ))}
                                </div>
                            </Section>
                        )}

                        {analysis.failed_test_explanation && (
                            <Section
                                icon={AlertTriangle}
                                title="Why the failed test case breaks"
                                subtitle="Use this to connect the bug with the input/output"
                            >
                                <div className="rounded-xl border border-border/80 bg-bg-hover/30 p-4 text-sm leading-7 text-text-primary">
                                    {analysis.failed_test_explanation}
                                </div>
                            </Section>
                        )}

                        <Section
                            icon={Lightbulb}
                            title="Step-by-step idea"
                            subtitle="Read this like a mini editorial, not a dense textbook answer"
                            accent
                        >
                            <div className="space-y-3">
                                {approachSteps.map((step, index) => (
                                    <div key={`${step}-${index}`} className="flex gap-4 rounded-xl border border-accent/10 bg-accent/5 p-4">
                                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent/15 text-xs font-bold text-accent">
                                            {index + 1}
                                        </div>
                                        <p className="text-sm leading-7 text-text-primary">{step}</p>
                                    </div>
                                ))}
                            </div>
                        </Section>

                        {analysis.improved_code && (
                            <Section
                                icon={Code2}
                                title="Reference solution"
                                subtitle="Use this to compare structure, not to blindly copy"
                                defaultOpen={false}
                            >
                                <div className="group relative overflow-hidden rounded-xl border border-white/10 shadow-2xl">
                                    <div className="flex items-center gap-2 border-b border-white/5 bg-[#1e1e1e] px-4 py-3">
                                        <div className="h-3 w-3 rounded-full bg-red-500/80" />
                                        <div className="h-3 w-3 rounded-full bg-amber-500/80" />
                                        <div className="h-3 w-3 rounded-full bg-emerald-500/80" />
                                        <div className="flex-1 pl-2">
                                            <span className="font-mono text-[10px] uppercase tracking-widest text-white/40">
                                                solution.optimal
                                            </span>
                                        </div>
                                    </div>
                                    <pre className="custom-scrollbar m-0 overflow-x-auto bg-[#141414] p-5 pt-4 font-mono text-[13px] leading-relaxed text-[#d4d4d4]">
                                        <code>{analysis.improved_code}</code>
                                    </pre>
                                </div>
                            </Section>
                        )}

                        {learnings && learnings.length > 0 && (
                            <Section
                                icon={Sparkles}
                                title="What to remember next time"
                                subtitle="Short lessons you can reuse in similar problems"
                            >
                                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                                    {learnings.map((tip, i) => (
                                        <div
                                            key={i}
                                            className="cursor-default rounded-xl border border-white/5 bg-bg-hover/50 p-4 transition-colors hover:border-accent/40 hover:bg-accent/5"
                                        >
                                            <div className="mb-2 flex items-center gap-2">
                                                <span className="text-accent">
                                                    <Sparkles size={15} />
                                                </span>
                                                <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-text-muted">
                                                    Takeaway {i + 1}
                                                </p>
                                            </div>
                                            <p className="text-sm leading-7 text-text-primary">{tip}</p>
                                        </div>
                                    ))}
                                </div>
                            </Section>
                        )}

                        <div className="h-4" />
                    </div>
                </div>

                <div className="flex items-center justify-between border-t border-white/10 bg-bg-surface px-8 py-5 backdrop-blur-md shrink-0">
                    <p className="text-xs font-medium text-text-muted">
                        Use the review to understand the pattern, the edge cases, and the reason behind the final verdict.
                    </p>
                    <button
                        onClick={onClose}
                        className="rounded-xl bg-gradient-to-r from-accent to-accent/80 px-8 py-2.5 text-sm font-bold text-white outline-none transition-all hover:-translate-y-0.5 hover:shadow-[0_6px_25px_rgba(102,126,234,0.6)] shadow-[0_4px_15px_rgba(102,126,234,0.4)]"
                    >
                        Back to Editor
                    </button>
                </div>
            </motion.div>
        </motion.div>
    );
}
