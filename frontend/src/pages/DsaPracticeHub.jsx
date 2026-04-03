import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Search, Building2, ChevronRight, Briefcase, Terminal, Activity
} from 'lucide-react';
import { COMPANIES, COMPANY_CATEGORIES } from '../utils/companies';
import CompanyLogo from '../components/ui/CompanyLogo';

const ITEMS_PER_PAGE = 12;

export default function DsaPracticeHub() {
    const navigate = useNavigate();
    const [search, setSearch] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('All');
    const [visibleCount, setVisibleCount] = useState(ITEMS_PER_PAGE);

    const categoryCounts = useMemo(() => {
        const counts = {};
        COMPANIES.forEach((c) => {
            counts[c.category] = (counts[c.category] || 0) + 1;
        });
        counts.All = COMPANIES.length;
        return counts;
    }, []);

    const filtered = useMemo(() => {
        return COMPANIES.filter((c) => {
            const matchesSearch = c.name.toLowerCase().includes(search.toLowerCase());
            const matchesCategory = selectedCategory === 'All' || c.category === selectedCategory;
            return matchesSearch && matchesCategory;
        });
    }, [search, selectedCategory]);

    const visibleCompanies = filtered.slice(0, visibleCount);
    const hasMore = visibleCount < filtered.length;

    const handleLoadMore = () => {
        setVisibleCount((prev) => prev + ITEMS_PER_PAGE);
    };

    const handleCategoryChange = (cat) => {
        setSelectedCategory(cat);
        setVisibleCount(ITEMS_PER_PAGE);
    };

    // Map category to short display label for cards
    const categoryShortLabel = (cat) => {
        const map = {
            'FAANG+': 'FAANG+',
            'Big Tech': 'BIG TECH',
            'Finance & Trading': 'FINANCE',
            'Indian IT': 'INDIAN IT',
            'Product (India)': 'PRODUCT (IN)',
            'Product (Global)': 'PRODUCT (GLB)',
            'Consulting': 'CONSULTING',
        };
        return map[cat] || cat.toUpperCase();
    };

    // Sidebar category items (skip 'All', show it separately)
    const sidebarCategories = COMPANY_CATEGORIES.filter((c) => c !== 'All');

    return (
        <div className="dsa-hub">
            <div className="dsa-hub__inner">
                {/* ── Header ──────────────────────────────── */}
                <motion.div
                    initial={{ opacity: 0, y: -12 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="dsa-hub__header"
                >
                    <div className="dsa-hub__header-left">
                        <span className="dsa-hub__kicker">Practice map</span>
                        <h1 className="dsa-hub__title">
                            Company Hub
                            <span className="dsa-hub__title-meta">
                                / {filtered.length} active systems
                            </span>
                        </h1>
                    </div>
                    <div className="dsa-hub__search-wrap">
                        <Search size={15} className="dsa-hub__search-icon" />
                        <input
                            type="text"
                            placeholder="Query system identifier..."
                            value={search}
                            onChange={(e) => {
                                setSearch(e.target.value);
                                setVisibleCount(ITEMS_PER_PAGE);
                            }}
                            className="dsa-hub__search-input"
                        />
                    </div>
                </motion.div>

                {/* ── Body: Sidebar + Grid ─────────────────── */}
                <div className="dsa-hub__body">
                    {/* Sidebar */}
                    <motion.aside
                        initial={{ opacity: 0, x: -16 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.08 }}
                        className="dsa-hub__sidebar"
                    >
                        <p className="dsa-hub__sidebar-title">Sector Classification</p>

                        {/* All Systems */}
                        <button
                            onClick={() => handleCategoryChange('All')}
                            className={`dsa-hub__cat-btn ${selectedCategory === 'All' ? 'dsa-hub__cat-btn--active' : ''}`}
                        >
                            <span>All Systems</span>
                            <span className="dsa-hub__cat-count">{categoryCounts.All}</span>
                        </button>

                        {sidebarCategories.map((cat) => (
                            <button
                                key={cat}
                                onClick={() => handleCategoryChange(cat)}
                                className={`dsa-hub__cat-btn ${selectedCategory === cat ? 'dsa-hub__cat-btn--active' : ''}`}
                            >
                                <span>{cat}</span>
                                <span className="dsa-hub__cat-count">{categoryCounts[cat] || 0}</span>
                            </button>
                        ))}

                        {/* Forge Intel panel */}
                        <div className="dsa-hub__intel">
                            <div className="dsa-hub__intel-header">
                                <Terminal size={12} />
                                <span>Forge Intel</span>
                            </div>
                            <div className="dsa-hub__intel-row">
                                <span className="dsa-hub__intel-label">Companies</span>
                                <span className="dsa-hub__intel-value dsa-hub__intel-value--accent">
                                    {COMPANIES.length} Total
                                </span>
                            </div>
                            <div className="dsa-hub__intel-row">
                                <span className="dsa-hub__intel-label">Categories</span>
                                <span className="dsa-hub__intel-value">
                                    {sidebarCategories.length} Sectors
                                </span>
                            </div>
                        </div>
                    </motion.aside>

                    {/* Main Grid */}
                    <motion.main
                        initial={{ opacity: 0, y: 16 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.12 }}
                        className="dsa-hub__main"
                    >
                        {filtered.length === 0 ? (
                            <div className="dsa-hub__empty">
                                <Briefcase size={40} className="dsa-hub__empty-icon" />
                                <p className="dsa-hub__empty-title">No systems found</p>
                                <p className="dsa-hub__empty-sub">Adjust search query or sector filters</p>
                            </div>
                        ) : (
                            <>
                                <div className="dsa-hub__grid">
                                    <AnimatePresence mode="popLayout">
                                        {visibleCompanies.map((company, idx) => (
                                            <motion.div
                                                key={company.id}
                                                layout
                                                initial={{ opacity: 0, y: 20, scale: 0.97 }}
                                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                                exit={{ opacity: 0, scale: 0.95 }}
                                                transition={{ delay: Math.min(idx * 0.025, 0.4), duration: 0.35 }}
                                                onClick={() => navigate(`/company/${company.id}`)}
                                                className="dsa-hub__card"
                                            >
                                                <div className="dsa-hub__card-logo-wrap">
                                                    <CompanyLogo
                                                        company={company}
                                                        size="lg"
                                                        roundedClassName="rounded-xl"
                                                        className="dsa-hub__card-logo"
                                                    />
                                                </div>
                                                <h3 className="dsa-hub__card-name">{company.name}</h3>
                                                <span className="dsa-hub__card-category">
                                                    {categoryShortLabel(company.category)}
                                                </span>
                                                {/* Hover chevron */}
                                                <div className="dsa-hub__card-chevron">
                                                    <ChevronRight size={16} />
                                                </div>
                                            </motion.div>
                                        ))}
                                    </AnimatePresence>
                                </div>

                                {hasMore && (
                                    <motion.div
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        className="dsa-hub__load-more-wrap"
                                    >
                                        <button
                                            onClick={handleLoadMore}
                                            className="dsa-hub__load-more-btn"
                                        >
                                            Initialize Additional Nodes
                                        </button>
                                    </motion.div>
                                )}
                            </>
                        )}
                    </motion.main>
                </div>
            </div>
        </div>
    );
}
