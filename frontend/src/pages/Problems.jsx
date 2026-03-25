import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
    Search, BookOpen, Filter, ChevronRight, Code2, Tag,
} from 'lucide-react';
import { problemApi } from '../api/auth';
import Badge from '../components/ui/Badge';

const DIFFICULTY_COLORS = {
    easy: 'green',
    medium: 'yellow',
    hard: 'red',
};

function extractTopic(description) {
    const match = description?.match(/\*\*Topic:\s*(.+?)\*\*/);
    return match ? match[1].trim() : 'General';
}

export default function Problems() {
    const navigate = useNavigate();
    const [search, setSearch] = useState('');
    const [selectedTopic, setSelectedTopic] = useState('All');
    const [selectedDifficulty, setSelectedDifficulty] = useState('All');

    const { data: problems = [], isLoading } = useQuery({
        queryKey: ['problems'],
        queryFn: problemApi.getAll,
    });

    // Extract unique topics
    const topics = useMemo(() => {
        const topicSet = new Set(problems.map((p) => extractTopic(p.description)));
        return ['All', ...Array.from(topicSet).sort()];
    }, [problems]);

    // Filter problems
    const filtered = useMemo(() => {
        return problems.filter((p) => {
            const matchesSearch = p.title.toLowerCase().includes(search.toLowerCase());
            const matchesTopic = selectedTopic === 'All' || extractTopic(p.description) === selectedTopic;
            const matchesDifficulty = selectedDifficulty === 'All' || p.difficulty === selectedDifficulty;
            return matchesSearch && matchesTopic && matchesDifficulty;
        });
    }, [problems, search, selectedTopic, selectedDifficulty]);

    return (
        <div className="min-h-screen bg-bg-root pb-20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
                {/* Header */}
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
                    <div className="flex items-center gap-3 mb-1">
                        <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                            <BookOpen size={20} className="text-accent" />
                        </div>
                        <div>
                            <h1 className="text-2xl sm:text-3xl font-extrabold text-text-primary tracking-tight">
                                Problem Bank
                            </h1>
                            <p className="text-text-secondary text-sm">
                                {problems.length} problems available &middot; Practice at your pace
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* Filters Bar */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="mt-6 flex flex-col sm:flex-row gap-3"
                >
                    {/* Search */}
                    <div className="relative flex-1">
                        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                        <input
                            type="text"
                            placeholder="Search problems..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="w-full pl-10 pr-4 py-2.5 bg-bg-secondary border border-border rounded-lg text-sm text-text-primary placeholder-text-muted focus:border-accent focus:outline-none transition-colors"
                        />
                    </div>

                    {/* Topic Filter */}
                    <div className="relative">
                        <Tag size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none" />
                        <select
                            value={selectedTopic}
                            onChange={(e) => setSelectedTopic(e.target.value)}
                            className="appearance-none pl-9 pr-8 py-2.5 bg-bg-secondary border border-border rounded-lg text-sm text-text-primary focus:border-accent focus:outline-none transition-colors cursor-pointer"
                        >
                            {topics.map((t) => (
                                <option key={t} value={t} className="bg-bg-primary">{t}</option>
                            ))}
                        </select>
                        <Filter size={12} className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none" />
                    </div>

                    {/* Difficulty Filter */}
                    <div className="flex gap-1.5">
                        {['All', 'easy', 'medium', 'hard'].map((d) => (
                            <button
                                key={d}
                                onClick={() => setSelectedDifficulty(d)}
                                className={`px-3 py-2 rounded-lg text-xs font-semibold capitalize transition-all border ${
                                    selectedDifficulty === d
                                        ? 'bg-accent/10 border-accent/30 text-accent'
                                        : 'bg-bg-secondary border-border text-text-secondary hover:border-border-hover hover:text-text-primary'
                                }`}
                            >
                                {d}
                            </button>
                        ))}
                    </div>
                </motion.div>

                {/* Problem Table */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="mt-6 bg-bg-secondary border border-border rounded-xl overflow-hidden"
                >
                    {/* Header Row */}
                    <div className="hidden sm:grid grid-cols-[1fr_120px_100px_80px] gap-4 px-6 py-3 border-b border-border/60 text-xs font-semibold text-text-muted uppercase tracking-wider">
                        <span>Problem</span>
                        <span>Topic</span>
                        <span>Difficulty</span>
                        <span></span>
                    </div>

                    {isLoading ? (
                        <div className="divide-y divide-border/30">
                            {Array.from({ length: 8 }).map((_, i) => (
                                <div key={i} className="px-6 py-4 flex items-center gap-4">
                                    <div className="w-8 h-8 rounded-lg bg-bg-surface animate-pulse" />
                                    <div className="flex-1 space-y-2">
                                        <div className="h-4 w-48 bg-bg-surface rounded animate-pulse" />
                                        <div className="h-3 w-24 bg-bg-surface rounded animate-pulse" />
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : filtered.length === 0 ? (
                        <div className="py-16 text-center">
                            <Code2 size={40} className="mx-auto text-text-muted/40 mb-3" />
                            <p className="text-text-secondary text-sm font-medium">No problems found</p>
                            <p className="text-text-muted text-xs mt-1">Try adjusting your filters</p>
                        </div>
                    ) : (
                        <div className="divide-y divide-border/30">
                            {filtered.map((problem, idx) => {
                                const topic = extractTopic(problem.description);
                                return (
                                    <motion.div
                                        key={problem.id}
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: Math.min(idx * 0.02, 0.5) }}
                                        onClick={() => navigate(`/practice/${problem.id}`)}
                                        className="grid grid-cols-1 sm:grid-cols-[1fr_120px_100px_80px] gap-2 sm:gap-4 px-6 py-4 hover:bg-bg-hover/40 transition-colors cursor-pointer group items-center"
                                    >
                                        {/* Title */}
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center text-accent text-xs font-bold shrink-0">
                                                {idx + 1}
                                            </div>
                                            <span className="text-sm font-medium text-text-primary group-hover:text-accent transition-colors truncate">
                                                {problem.title}
                                            </span>
                                        </div>

                                        {/* Topic */}
                                        <span className="text-xs text-text-secondary font-medium truncate">
                                            {topic}
                                        </span>

                                        {/* Difficulty */}
                                        <div>
                                            <Badge color={DIFFICULTY_COLORS[problem.difficulty] || 'gray'}>
                                                {problem.difficulty}
                                            </Badge>
                                        </div>

                                        {/* Arrow */}
                                        <div className="hidden sm:flex justify-end">
                                            <ChevronRight size={16} className="text-text-muted group-hover:text-accent transition-colors" />
                                        </div>
                                    </motion.div>
                                );
                            })}
                        </div>
                    )}
                </motion.div>
            </div>
        </div>
    );
}
