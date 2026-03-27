import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    Search, Building2, ChevronRight, Briefcase,
} from 'lucide-react';
import { COMPANIES, COMPANY_CATEGORIES } from '../utils/companies';

export default function Problems() {
    const navigate = useNavigate();
    const [search, setSearch] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('All');

    const filtered = useMemo(() => {
        return COMPANIES.filter((c) => {
            const matchesSearch = c.name.toLowerCase().includes(search.toLowerCase());
            const matchesCategory = selectedCategory === 'All' || c.category === selectedCategory;
            return matchesSearch && matchesCategory;
        });
    }, [search, selectedCategory]);

    // Group companies by category for displaying counts
    const categoryCounts = useMemo(() => {
        const counts = {};
        COMPANIES.forEach((c) => {
            counts[c.category] = (counts[c.category] || 0) + 1;
        });
        counts['All'] = COMPANIES.length;
        return counts;
    }, []);

    return (
        <div className="min-h-screen bg-bg-root pb-20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
                {/* Header */}
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
                    <div className="flex items-center gap-3 mb-1">
                        <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                            <Building2 size={20} className="text-accent" />
                        </div>
                        <div>
                            <h1 className="text-2xl sm:text-3xl font-extrabold text-text-primary tracking-tight">
                                Company Hub
                            </h1>
                            <p className="text-text-secondary text-sm">
                                {COMPANIES.length} companies &middot; Practice company-wise questions
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* Filters Bar */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="mt-6 space-y-4"
                >
                    {/* Search */}
                    <div className="relative max-w-md">
                        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                        <input
                            type="text"
                            placeholder="Search companies..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="w-full pl-10 pr-4 py-2.5 bg-bg-secondary border border-border rounded-lg text-sm text-text-primary placeholder-text-muted focus:border-accent focus:outline-none transition-colors"
                        />
                    </div>

                    {/* Category Chips */}
                    <div className="flex flex-wrap gap-2">
                        {COMPANY_CATEGORIES.map((cat) => (
                            <button
                                key={cat}
                                onClick={() => setSelectedCategory(cat)}
                                className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all border ${
                                    selectedCategory === cat
                                        ? 'bg-accent/15 border-accent/40 text-accent shadow-sm shadow-accent/10'
                                        : 'bg-bg-secondary border-border text-text-secondary hover:border-border-hover hover:text-text-primary'
                                }`}
                            >
                                {cat}
                                <span className="ml-1.5 opacity-60">{categoryCounts[cat] || 0}</span>
                            </button>
                        ))}
                    </div>
                </motion.div>

                {/* Companies Grid */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="mt-8"
                >
                    {filtered.length === 0 ? (
                        <div className="py-16 text-center">
                            <Briefcase size={40} className="mx-auto text-text-muted/40 mb-3" />
                            <p className="text-text-secondary text-sm font-medium">No companies found</p>
                            <p className="text-text-muted text-xs mt-1">Try adjusting your search or filters</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                            {filtered.map((company, idx) => (
                                <motion.div
                                    key={company.id}
                                    initial={{ opacity: 0, y: 15 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: Math.min(idx * 0.02, 0.6) }}
                                    onClick={() => navigate(`/company/${company.id}`)}
                                    className="group relative bg-bg-secondary border border-border rounded-xl p-5 cursor-pointer transition-all duration-300 hover:border-border-hover hover:bg-bg-hover/40 hover:shadow-lg hover:shadow-black/20 hover:-translate-y-0.5"
                                >
                                    {/* Accent top line */}
                                    <div
                                        className="absolute top-0 left-4 right-4 h-[2px] rounded-b-full opacity-40 group-hover:opacity-80 transition-opacity"
                                        style={{ backgroundColor: company.color }}
                                    />

                                    <div className="flex items-start justify-between">
                                        <div className="flex items-center gap-3">
                                            {/* Logo / Emoji */}
                                            <div
                                                className="w-11 h-11 rounded-xl flex items-center justify-center text-xl shrink-0 transition-transform group-hover:scale-110"
                                                style={{ backgroundColor: `${company.color}15` }}
                                            >
                                                {company.logo}
                                            </div>
                                            <div className="min-w-0">
                                                <h3 className="text-sm font-bold text-text-primary group-hover:text-accent transition-colors truncate">
                                                    {company.name}
                                                </h3>
                                                <span
                                                    className="inline-block mt-1 px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider"
                                                    style={{
                                                        color: company.color,
                                                        backgroundColor: `${company.color}12`,
                                                    }}
                                                >
                                                    {company.category}
                                                </span>
                                            </div>
                                        </div>
                                        <ChevronRight
                                            size={16}
                                            className="text-text-muted group-hover:text-accent transition-all group-hover:translate-x-0.5 shrink-0 mt-1"
                                        />
                                    </div>

                                    {/* Footer */}
                                    <div className="mt-4 pt-3 border-t border-border/50 flex items-center justify-between">
                                        <span className="text-[11px] text-text-muted font-medium">
                                            Questions coming soon
                                        </span>
                                        <span
                                            className="w-2 h-2 rounded-full opacity-50"
                                            style={{ backgroundColor: company.color }}
                                        />
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    )}
                </motion.div>
            </div>
        </div>
    );
}
