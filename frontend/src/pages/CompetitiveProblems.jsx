import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { ArrowLeft, Check, Play, Trophy } from 'lucide-react';
import { problemApi } from '../api/auth';
import Badge from '../components/ui/Badge';

const ratingBuckets = ['all', '800', '900', '1000+'];

export default function CompetitiveProblems() {
    const navigate = useNavigate();
    const [ratingFilter, setRatingFilter] = useState('all');

    const { data: problems = [], isLoading } = useQuery({
        queryKey: ['problems'],
        queryFn: problemApi.getAll,
    });

    const cpProblems = useMemo(() => (
        problems
            .filter((problem) => problem.problem_type === 'cp')
            .sort((a, b) => (a.rating || 0) - (b.rating || 0) || a.title.localeCompare(b.title))
    ), [problems]);

    const filteredProblems = useMemo(() => {
        if (ratingFilter === 'all') return cpProblems;
        if (ratingFilter === '1000+') return cpProblems.filter((problem) => (problem.rating || 0) >= 1000);
        return cpProblems.filter((problem) => String(problem.rating || '') === ratingFilter);
    }, [cpProblems, ratingFilter]);

    const counts = useMemo(() => ({
        all: cpProblems.length,
        800: cpProblems.filter((problem) => problem.rating === 800).length,
        900: cpProblems.filter((problem) => problem.rating === 900).length,
        '1000+': cpProblems.filter((problem) => (problem.rating || 0) >= 1000).length,
    }), [cpProblems]);

    return (
        <div className="min-h-screen bg-bg-root pb-20">
            <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
                <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}>
                    <button
                        onClick={() => navigate('/problems')}
                        className="flex items-center gap-2 text-text-secondary hover:text-text-primary text-sm font-medium mb-6 transition-colors group"
                    >
                        <ArrowLeft size={16} className="group-hover:-translate-x-0.5 transition-transform" />
                        Back to practice modes
                    </button>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="paper-card p-6 sm:p-7 border-l-4 border-l-[#7ec4cf]"
                >
                    <div className="flex items-center gap-4">
                        <div className="w-14 h-14 rounded-[18px_14px_16px_12px] bg-[#7ec4cf]/12 flex items-center justify-center shadow-[0_6px_16px_rgba(0,0,0,0.18)]">
                            <Trophy size={24} className="text-[#7ec4cf]" />
                        </div>
                        <div>
                            <p className="editorial-kicker mb-2">Competitive programming</p>
                            <h1 className="text-2xl sm:text-3xl font-bold text-text-primary">Codeforces-style ladder</h1>
                            <p className="text-sm text-text-secondary mt-1">
                                Raw stdin/stdout problems grouped by rating, with no platform-side method boilerplate.
                            </p>
                        </div>
                    </div>
                </motion.div>

                <div className="mt-6 paper-card-soft p-4 sm:p-5">
                    <div className="flex flex-wrap gap-2">
                        {ratingBuckets.map((bucket) => (
                            <button
                                key={bucket}
                                onClick={() => setRatingFilter(bucket)}
                                className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-colors ${
                                    ratingFilter === bucket
                                        ? 'bg-bg-hover text-text-primary border-border-hover'
                                        : 'bg-bg-secondary text-text-secondary border-border hover:text-text-primary'
                                }`}
                            >
                                {bucket === 'all' ? 'All ratings' : bucket}
                                <span className="ml-1.5 opacity-70">{counts[bucket] || 0}</span>
                            </button>
                        ))}
                    </div>
                </div>

                <div className="mt-6 grid gap-4">
                    {isLoading ? (
                        <div className="flex justify-center py-12">
                            <div className="w-8 h-8 border-4 border-accent border-t-transparent rounded-full animate-spin"></div>
                        </div>
                    ) : filteredProblems.length === 0 ? (
                        <div className="paper-card-soft p-8 text-center">
                            <p className="text-text-secondary text-sm">No competitive programming problems found for this rating range.</p>
                        </div>
                    ) : filteredProblems.map((problem, idx) => (
                        <motion.div
                            key={problem.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 + idx * 0.05 }}
                            onClick={() => navigate(`/practice/${problem.id}`)}
                            className="group relative paper-card-soft hover:border-[#7ec4cf]/50 p-5 cursor-pointer transition-colors"
                        >
                            <div className="flex items-center justify-between gap-4">
                                <div className="flex items-start gap-3 min-w-0">
                                    <div
                                        className={`mt-0.5 h-5 w-5 shrink-0 rounded-md border flex items-center justify-center transition-colors ${
                                            problem.solved
                                                ? 'border-[#6fbf73] bg-[#6fbf73]/15 text-[#6fbf73]'
                                                : 'border-border text-transparent bg-bg-secondary'
                                        }`}
                                        title={problem.solved ? 'Solved' : 'Not solved yet'}
                                    >
                                        <Check className="w-3.5 h-3.5" />
                                    </div>
                                    <div className="min-w-0">
                                        <h3 className="text-base font-bold text-text-primary group-hover:text-[#7ec4cf] transition-colors pr-5">
                                            {problem.title}
                                        </h3>
                                        <div className="flex items-center gap-3 mt-2 text-xs text-text-muted">
                                            <span className="px-2.5 py-1 rounded-full border border-[#7ec4cf]/30 bg-[#7ec4cf]/10 text-[#7ec4cf] font-semibold">
                                                {problem.rating}
                                            </span>
                                            <Badge color={problem.difficulty === 'easy' ? 'green' : problem.difficulty === 'medium' ? 'yellow' : 'red'}>
                                                {problem.difficulty}
                                            </Badge>
                                            <span className="px-2 py-1 rounded-full border border-border text-text-secondary">
                                                stdin / stdout
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div className="w-10 h-10 rounded-lg bg-[#7ec4cf]/12 flex items-center justify-center translate-x-3 opacity-0 group-hover:translate-x-0 group-hover:opacity-100 transition-all">
                                    <Play className="w-4 h-4 text-[#7ec4cf] translate-x-0.5" />
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    );
}
