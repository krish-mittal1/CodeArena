import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { ArrowLeft, Check, Play, Trophy, Search, ChevronRight, Code2, Zap, BarChart3 } from 'lucide-react';
import { problemApi } from '../api/auth';

const ratingBuckets = ['all', '800', '900', '1000+'];

const Fade = ({ children, delay = 0, className = '' }) => (
    <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45, delay, ease: [0.22, 1, 0.36, 1] }}
        className={className}
    >
        {children}
    </motion.div>
);

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

    const solvedCount = cpProblems.filter(p => p.solved).length;
    const easyCount = cpProblems.filter(p => p.difficulty === 'easy').length;
    const mediumCount = cpProblems.filter(p => p.difficulty === 'medium').length;
    const hardCount = cpProblems.filter(p => p.difficulty === 'hard').length;

    return (
        <div className="cpg">
            <div className="cpg__inner">

                {/* Back */}
                <Fade>
                    <button onClick={() => navigate('/problems')} className="cpg__back">
                        <ArrowLeft size={14} />
                        Back to practice modes
                    </button>
                </Fade>

                {/* ═══ Hero Banner ═══ */}
                <Fade delay={0.04}>
                    <div className="cpg__hero paper-card grain-panel">
                        <div className="cpg__hero-accent" />
                        <div className="cpg__hero-content">
                            <div className="cpg__hero-icon">
                                <Trophy size={26} />
                            </div>
                            <div className="cpg__hero-text">
                                <span className="cpg__kicker">COMPETITIVE PROGRAMMING</span>
                                <h1 className="cpg__title">Codeforces-Style Ladder</h1>
                                <p className="cpg__subtitle">
                                    Raw stdin/stdout problems sorted by rating. No boilerplate — just algorithms.
                                </p>
                            </div>
                        </div>

                        {/* Stats strip inside hero */}
                        <div className="cpg__hero-stats">
                            <div className="cpg__hero-stat">
                                <Code2 size={14} className="text-accent" />
                                <span className="cpg__hero-stat-val">{cpProblems.length}</span>
                                <span className="cpg__hero-stat-label">PROBLEMS</span>
                            </div>
                            <div className="cpg__hero-stat-divider" />
                            <div className="cpg__hero-stat">
                                <Check size={14} className="text-win" />
                                <span className="cpg__hero-stat-val">{solvedCount}</span>
                                <span className="cpg__hero-stat-label">SOLVED</span>
                            </div>
                            <div className="cpg__hero-stat-divider" />
                            <div className="cpg__hero-stat">
                                <BarChart3 size={14} className="text-draw" />
                                <span className="cpg__hero-stat-val">
                                    {cpProblems.length > 0 ? Math.round((solvedCount / cpProblems.length) * 100) : 0}%
                                </span>
                                <span className="cpg__hero-stat-label">PROGRESS</span>
                            </div>
                        </div>
                    </div>
                </Fade>

                {/* ═══ Difficulty Breakdown ═══ */}
                <Fade delay={0.08}>
                    <div className="cpg__diff-strip">
                        <div className="cpg__diff-item">
                            <span className="cpg__diff-dot cpg__diff-dot--easy" />
                            <span className="cpg__diff-label">Easy</span>
                            <span className="cpg__diff-count">{easyCount}</span>
                        </div>
                        <div className="cpg__diff-item">
                            <span className="cpg__diff-dot cpg__diff-dot--medium" />
                            <span className="cpg__diff-label">Medium</span>
                            <span className="cpg__diff-count">{mediumCount}</span>
                        </div>
                        <div className="cpg__diff-item">
                            <span className="cpg__diff-dot cpg__diff-dot--hard" />
                            <span className="cpg__diff-label">Hard</span>
                            <span className="cpg__diff-count">{hardCount}</span>
                        </div>
                    </div>
                </Fade>

                {/* ═══ Filters & Search ═══ */}
                <Fade delay={0.1}>
                    <div className="cpg__controls">
                        <div className="cpg__filters">
                            {ratingBuckets.map((bucket) => (
                                <button
                                    key={bucket}
                                    onClick={() => setRatingFilter(bucket)}
                                    className={`cpg__filter-btn ${ratingFilter === bucket ? 'cpg__filter-btn--active' : ''}`}
                                >
                                    {bucket === 'all' ? 'All Ratings' : `Rating ${bucket}`}
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
                    </div>
                </Fade>

                {/* ═══ Problem List ═══ */}
                <div className="cpg__list">
                    {isLoading ? (
                        <div className="cpg__loading">
                            {Array.from({ length: 5 }).map((_, i) => (
                                <div key={i} className="cpg__skel-row">
                                    <div className="cpg__skel-check" />
                                    <div className="cpg__skel-body">
                                        <div className="cpg__skel-title" />
                                        <div className="cpg__skel-tags">
                                            <div className="cpg__skel-tag" />
                                            <div className="cpg__skel-tag cpg__skel-tag--sm" />
                                            <div className="cpg__skel-tag" />
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : filteredProblems.length === 0 ? (
                        <div className="cpg__empty">
                            <div className="cpg__empty-icon">
                                <Trophy size={36} />
                            </div>
                            <p className="cpg__empty-title">No problems found</p>
                            <p className="cpg__empty-sub">Try adjusting the filters or search term</p>
                        </div>
                    ) : (
                        filteredProblems.map((problem, idx) => (
                            <Fade key={problem.id} delay={0.08 + idx * 0.025}>
                                <div
                                    onClick={() => navigate(`/practice/${problem.id}`)}
                                    className={`cpg__row group ${problem.solved ? 'cpg__row--solved' : ''}`}
                                >
                                    {/* Left accent */}
                                    <div className={`cpg__row-accent ${
                                        problem.difficulty === 'easy' ? 'cpg__row-accent--easy'
                                            : problem.difficulty === 'medium' ? 'cpg__row-accent--medium'
                                                : 'cpg__row-accent--hard'
                                    }`} />

                                    {/* Checkbox */}
                                    <div className={`cpg__check ${problem.solved ? 'cpg__check--solved' : ''}`}>
                                        <Check className="cpg__check-icon" />
                                    </div>

                                    {/* Content */}
                                    <div className="cpg__row-content">
                                        <h3 className="cpg__row-title">{problem.title}</h3>
                                        <div className="cpg__row-tags">
                                            <span className="cpg__tag cpg__tag--rating">
                                                <Zap size={10} />
                                                {problem.rating || '—'}
                                            </span>
                                            <span className={`cpg__tag cpg__tag--diff cpg__tag--${problem.difficulty}`}>
                                                {problem.difficulty}
                                            </span>
                                            <span className="cpg__tag cpg__tag--io">stdin / stdout</span>
                                        </div>
                                    </div>

                                    {/* Play / Arrow */}
                                    <div className="cpg__action">
                                        <ChevronRight size={18} className="cpg__action-arrow" />
                                        <div className="cpg__action-play">
                                            <Play size={14} />
                                        </div>
                                    </div>
                                </div>
                            </Fade>
                        ))
                    )}
                </div>

                {/* ═══ Footer Info ═══ */}
                {!isLoading && filteredProblems.length > 0 && (
                    <Fade delay={0.3}>
                        <div className="cpg__footer">
                            <span>Showing {filteredProblems.length} of {cpProblems.length} problems</span>
                            <span>·</span>
                            <span>stdin/stdout format</span>
                            <span>·</span>
                            <span>Competitive programming mode</span>
                        </div>
                    </Fade>
                )}
            </div>
        </div>
    );
}
