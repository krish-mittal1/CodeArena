import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { ArrowLeft, Check, Play, Trophy, Search } from 'lucide-react';
import { problemApi } from '../api/auth';

const ratingBuckets = ['all', '800', '900', '1000+'];

export default function CompetitiveProblems() {
    const navigate = useNavigate();
    const [ratingFilter, setRatingFilter] = useState('all');
    const [search, setSearch] = useState('');

    const { data: problems = [], isLoading } = useQuery({
        queryKey: ['problems'],
        queryFn: problemApi.getAll,
    });

    const cpProblems = useMemo(() => (
        problems
            .filter((p) => p.problem_type === 'cp')
            .sort((a, b) => (a.rating || 0) - (b.rating || 0) || a.title.localeCompare(b.title))
    ), [problems]);

    const filteredProblems = useMemo(() => {
        let result = cpProblems;
        if (ratingFilter !== 'all') {
            if (ratingFilter === '1000+') result = result.filter((p) => (p.rating || 0) >= 1000);
            else result = result.filter((p) => String(p.rating || '') === ratingFilter);
        }
        if (search.trim()) {
            const q = search.toLowerCase();
            result = result.filter((p) => p.title.toLowerCase().includes(q));
        }
        return result;
    }, [cpProblems, ratingFilter, search]);

    const counts = useMemo(() => ({
        all: cpProblems.length,
        800: cpProblems.filter((p) => p.rating === 800).length,
        900: cpProblems.filter((p) => p.rating === 900).length,
        '1000+': cpProblems.filter((p) => (p.rating || 0) >= 1000).length,
    }), [cpProblems]);

    return (
        <div className="cpg">
            <div className="cpg__inner">

                {/* Back */}
                <motion.div initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}>
                    <button onClick={() => navigate('/problems')} className="cpg__back">
                        <ArrowLeft size={15} />
                        BACK_TO_PRACTICE
                    </button>
                </motion.div>

                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="cpg__header"
                >
                    <div className="cpg__header-left">
                        <div className="cpg__header-icon">
                            <Trophy size={22} />
                        </div>
                        <div>
                            <span className="cpg__kicker">COMPETITIVE PROGRAMMING</span>
                            <h1 className="cpg__title">Codeforces-Style Ladder</h1>
                            <p className="cpg__subtitle">
                                Raw stdin/stdout problems · Grouped by rating · {cpProblems.length} problems loaded
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* Filters & Search */}
                <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.06 }}
                    className="cpg__controls"
                >
                    <div className="cpg__filters">
                        {ratingBuckets.map((bucket) => (
                            <button
                                key={bucket}
                                onClick={() => setRatingFilter(bucket)}
                                className={`cpg__filter-btn ${ratingFilter === bucket ? 'cpg__filter-btn--active' : ''}`}
                            >
                                {bucket === 'all' ? 'All' : bucket}
                                <span className="cpg__filter-count">{counts[bucket] || 0}</span>
                            </button>
                        ))}
                    </div>
                    <div className="cpg__search-wrap">
                        <Search size={14} className="cpg__search-icon" />
                        <input
                            type="text"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            placeholder="Search problems..."
                            className="cpg__search-input"
                        />
                    </div>
                </motion.div>

                {/* Problem List */}
                <div className="cpg__list">
                    {isLoading ? (
                        <div className="cpg__loading">
                            <div className="cpg__spinner" />
                        </div>
                    ) : filteredProblems.length === 0 ? (
                        <div className="cpg__empty">
                            <Trophy size={32} className="text-text-muted/30 mb-2" />
                            <p className="text-text-secondary text-sm font-medium">No problems found</p>
                            <p className="text-text-muted text-xs mt-1">Try changing the rating filter or search term</p>
                        </div>
                    ) : (
                        filteredProblems.map((problem, idx) => (
                            <motion.div
                                key={problem.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.06 + idx * 0.03 }}
                            >
                                <div
                                    onClick={() => navigate(`/practice/${problem.id}`)}
                                    className="cpg__row group"
                                >
                                    {/* Checkbox */}
                                    <div
                                        className={`cpg__check ${problem.solved ? 'cpg__check--solved' : ''}`}
                                        title={problem.solved ? 'Solved' : 'Not solved yet'}
                                    >
                                        <Check className="cpg__check-icon" />
                                    </div>

                                    {/* Content */}
                                    <div className="cpg__row-content">
                                        <h3 className="cpg__row-title">{problem.title}</h3>
                                        <div className="cpg__row-tags">
                                            <span className="cpg__tag cpg__tag--rating">{problem.rating || '—'}</span>
                                            <span className={`cpg__tag cpg__tag--diff cpg__tag--${problem.difficulty}`}>
                                                {problem.difficulty}
                                            </span>
                                            <span className="cpg__tag cpg__tag--io">stdin / stdout</span>
                                        </div>
                                    </div>

                                    {/* Play button */}
                                    <div className="cpg__play">
                                        <Play size={16} />
                                    </div>
                                </div>
                            </motion.div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
