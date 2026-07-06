import { useMemo, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Building2, Check, Clock, Code2, Play, Search, Terminal, ChevronRight, Zap } from 'lucide-react';
import { COMPANIES } from '../utils/companies';
import { problemApi } from '../api/auth';
import CompanyLogo from '../components/ui/CompanyLogo';
import { getProblemMetadata, DEFAULT_PROBLEM_COMPANIES } from '../data/problemMetadata';

function normalizeCompanyName(value) {
    return (value || '').toLowerCase().replace(/[^a-z0-9]/g, '');
}

function companyNameMatches(datasetName, mappedName) {
    const dataset = normalizeCompanyName(datasetName);
    const mapped = normalizeCompanyName(mappedName);

    if (!dataset || !mapped) return false;
    return dataset === mapped || dataset.includes(mapped) || mapped.includes(dataset);
}

    };

    const companyProblems = problems
        .filter((p) => p.problem_type !== 'cp')
        .map((p) => {
            let title = p.title;
            if (title.includes("Spiral")) title = "Print the matrix in spiral manner";

            const metadata = getProblemMetadata(title) || { topic: "Arrays", companies: DEFAULT_PROBLEM_COMPANIES };

            const isMappedToCompany = metadata.companies.some((mappedCompany) =>
                companyNameMatches(company?.name, mappedCompany)
            );

            if (!isMappedToCompany) return null;

            return {
                ...p,
                topic: metadata.topic,
            };
        })
        .filter(Boolean);

    const difficultyCounts = useMemo(() => {
        const counts = { all: companyProblems.length, easy: 0, medium: 0, hard: 0 };
        companyProblems.forEach((problem) => {
            const key = (problem.difficulty || '').toLowerCase();
            if (counts[key] !== undefined) counts[key] += 1;
        });
        return counts;
    }, [companyProblems]);

    const filteredProblems = useMemo(() => {
        return companyProblems.filter((problem) => {
            const matchesDifficulty =
                difficultyFilter === 'all' ||
                (problem.difficulty || '').toLowerCase() === difficultyFilter;
            const matchesTopic =
                topicFilter === 'all' ||
                (problem.topic || '').toLowerCase() === topicFilter;
            const matchesSearch =
                !searchQuery ||
                problem.title.toLowerCase().includes(searchQuery.toLowerCase());
            return matchesDifficulty && matchesTopic && matchesSearch;
        });
    }, [companyProblems, difficultyFilter, topicFilter, searchQuery]);

    const topicOptions = useMemo(() => {
        const uniqueTopics = [...new Set(companyProblems.map((problem) => problem.topic).filter(Boolean))];
        return ['all', ...uniqueTopics.map((topic) => topic.toLowerCase())];
    }, [companyProblems]);

    const topicCounts = useMemo(() => {
        const counts = { all: companyProblems.length };
        companyProblems.forEach((problem) => {
            const key = (problem.topic || '').toLowerCase();
            if (!key) return;
            counts[key] = (counts[key] || 0) + 1;
        });
        return counts;
    }, [companyProblems]);

    const difficultyColor = (d) => {
        const dl = (d || '').toLowerCase();
        if (dl === 'easy') return '#6fbf73';
        if (dl === 'medium') return '#c39a4f';
        return '#c65a49';
    };

    if (!company) {
        return (
            <div className="cprob">
                <div className="cprob__inner" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
                    <div style={{ textAlign: 'center' }}>
                        <Building2 size={40} style={{ margin: '0 auto 12px', opacity: 0.3, color: 'var(--color-text-muted)' }} />
                        <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', fontWeight: 600 }}>System not found</p>
                        <button
                            onClick={() => navigate('/practice/dsa')}
                            className="cprob__back-btn"
                            style={{ marginTop: '1rem' }}
                        >
                            <ArrowLeft size={14} />
                            Return to Company Hub
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="cprob">
            <div className="cprob__inner">
                {/* ── Header ──────────────────────────────── */}
                <motion.div
                    initial={{ opacity: 0, y: -12 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="cprob__header"
                >
                    <button
                        onClick={() => navigate('/practice/dsa')}
                        className="cprob__back-btn"
                    >
                        <ArrowLeft size={14} />
                        Company Hub
                    </button>

                    <div className="cprob__header-main">
                        <div className="cprob__header-left">
                            <CompanyLogo
                                company={company}
                                size="lg"
                                roundedClassName="rounded-xl"
                                className="cprob__company-logo"
                            />
                            <div>
                                <span className="cprob__kicker">System Profile</span>
                                <h1 className="cprob__title">{company.name}</h1>
                                <p className="cprob__subtitle">
                                    {companyProblems.length} challenge{companyProblems.length === 1 ? '' : 's'} mapped
                                    <span className="cprob__subtitle-sep">·</span>
                                    {topicOptions.length - 1} topic{topicOptions.length - 1 === 1 ? '' : 's'}
                                </p>
                            </div>
                        </div>

                        <div className="cprob__search-wrap">
                            <Search size={15} className="cprob__search-icon" />
                            <input
                                type="text"
                                placeholder="Search challenges..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="cprob__search-input"
                            />
                        </div>
                    </div>
                </motion.div>

                {/* ── Body ────────────────────────────────── */}
                {isLoading ? (
                    <div className="cprob__loading">
                        <div className="cprob__spinner" />
                    </div>
                ) : companyProblems.length > 0 ? (
                    <div className="cprob__body">
                        {/* Sidebar */}
                        <motion.aside
                            initial={{ opacity: 0, x: -16 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.08 }}
                            className="cprob__sidebar"
                        >
                            {/* Difficulty */}
                            <p className="cprob__sidebar-title">Threat Level</p>
                            {[
                                { key: 'all', label: 'All Levels' },
                                { key: 'easy', label: 'Easy' },
                                { key: 'medium', label: 'Medium' },
                                { key: 'hard', label: 'Hard' },
                            ].map((chip) => (
                                <button
                                    key={chip.key}
                                    onClick={() => setDifficultyFilter(chip.key)}
                                    className={`cprob__filter-btn ${difficultyFilter === chip.key ? 'cprob__filter-btn--active' : ''}`}
                                >
                                    {chip.key !== 'all' && (
                                        <span
                                            className="cprob__diff-dot"
                                            style={{ background: difficultyColor(chip.key) }}
                                        />
                                    )}
                                    <span>{chip.label}</span>
                                    <span className="cprob__filter-count">{difficultyCounts[chip.key]}</span>
                                </button>
                            ))}

                            {/* Topics */}
                            <p className="cprob__sidebar-title" style={{ marginTop: '1.5rem' }}>
                                Algorithm Class
                            </p>
                            {topicOptions.map((topicKey) => (
                                <button
                                    key={topicKey}
                                    onClick={() => setTopicFilter(topicKey)}
                                    className={`cprob__filter-btn ${topicFilter === topicKey ? 'cprob__filter-btn--active' : ''}`}
                                >
                                    <span>
                                        {topicKey === 'all'
                                            ? 'All Topics'
                                            : topicKey.split(' ').map((w) => w[0].toUpperCase() + w.slice(1)).join(' ')}
                                    </span>
                                    <span className="cprob__filter-count">{topicCounts[topicKey] || 0}</span>
                                </button>
                            ))}

                            {/* Stats */}
                            <div className="cprob__stats-panel">
                                <div className="cprob__stats-header">
                                    <Terminal size={12} />
                                    <span>Intel Summary</span>
                                </div>
                                <div className="cprob__stats-row">
                                    <span className="cprob__stats-label">Total</span>
                                    <span className="cprob__stats-value cprob__stats-value--accent">{companyProblems.length}</span>
                                </div>
                                <div className="cprob__stats-row">
                                    <span className="cprob__stats-label">Showing</span>
                                    <span className="cprob__stats-value">{filteredProblems.length}</span>
                                </div>
                                <div className="cprob__stats-row">
                                    <span className="cprob__stats-label">Topics</span>
                                    <span className="cprob__stats-value">{topicOptions.length - 1}</span>
                                </div>
                            </div>
                        </motion.aside>

                        {/* Problem List */}
                        <motion.main
                            initial={{ opacity: 0, y: 16 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.12 }}
                            className="cprob__main"
                        >
                            {/* Column headers */}
                            <div className="cprob__list-header">
                                <span className="cprob__list-header-status">Status</span>
                                <span className="cprob__list-header-title">Challenge</span>
                                <span className="cprob__list-header-diff">Level</span>
                                <span className="cprob__list-header-topic">Topic</span>
                            </div>

                            {filteredProblems.length === 0 ? (
                                <div className="cprob__empty">
                                    <p>No challenges match current filters</p>
                                </div>
                            ) : (
                                <div className="cprob__list">
                                    <AnimatePresence mode="popLayout">
                                        {filteredProblems.map((prob, idx) => (
                                            <motion.div
                                                key={prob.id}
                                                layout
                                                initial={{ opacity: 0, y: 8 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                exit={{ opacity: 0, y: -8 }}
                                                transition={{ delay: Math.min(idx * 0.03, 0.5), duration: 0.3 }}
                                                onClick={() => navigate(`/practice/${prob.id}`)}
                                                className="cprob__row"
                                            >
                                                {/* Status */}
                                                <div className="cprob__row-status">
                                                    <div className={`cprob__check ${prob.solved ? 'cprob__check--solved' : ''}`}>
                                                        <Check className="cprob__check-icon" />
                                                    </div>
                                                </div>

                                                {/* Title */}
                                                <div className="cprob__row-title">
                                                    <h3 className="cprob__row-name">{prob.title}</h3>
                                                </div>

                                                {/* Difficulty */}
                                                <div className="cprob__row-diff">
                                                    <span
                                                        className="cprob__diff-badge"
                                                        style={{
                                                            color: difficultyColor(prob.difficulty),
                                                            background: `${difficultyColor(prob.difficulty)}15`,
                                                            borderColor: `${difficultyColor(prob.difficulty)}30`,
                                                        }}
                                                    >
                                                        {prob.difficulty}
                                                    </span>
                                                </div>

                                                {/* Topic */}
                                                <div className="cprob__row-topic">
                                                    {prob.topic && (
                                                        <span className="cprob__topic-badge">
                                                            {prob.topic}
                                                        </span>
                                                    )}
                                                </div>

                                                {/* Hover arrow */}
                                                <div className="cprob__row-arrow">
                                                    <ChevronRight size={16} />
                                                </div>
                                            </motion.div>
                                        ))}
                                    </AnimatePresence>
                                </div>
                            )}
                        </motion.main>
                    </div>
                ) : (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.15 }}
                        className="cprob__coming-soon"
                    >
                        <div className="cprob__coming-soon-icon">
                            <Clock size={28} />
                        </div>
                        <h2 className="cprob__coming-soon-title">Challenges Incoming</h2>
                        <p className="cprob__coming-soon-desc">
                            We're curating the most frequently asked coding questions from{' '}
                            <strong>{company.name}</strong> interviews and online assessments.
                            Check back soon!
                        </p>
                        <div className="cprob__coming-soon-meta">
                            <span><Code2 size={14} /> OA Questions</span>
                            <span className="cprob__coming-soon-sep" />
                            <span><Building2 size={14} /> Interview Rounds</span>
                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    );
}
