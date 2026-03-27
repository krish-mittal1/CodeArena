import { useState, useRef, useEffect } from 'react';
import { Link, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Swords, LayoutDashboard, History, User, Bell, Settings, LogOut, ChevronDown, Building2, Menu, X
} from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { useBattleStore } from '../../stores/battleStore';
import { useLogout } from '../../hooks/useAuth';

export default function Navbar() {
    const { user, isAuthenticated } = useAuthStore();
    const matchId = useBattleStore((s) => s.matchId);
    const handleLogout = useLogout();
    const navigate = useNavigate();
    const location = useLocation();
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const dropdownRef = useRef(null);

    useEffect(() => {
        const handler = (e) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setDropdownOpen(false);
            }
        };
        document.addEventListener('mousedown', handler);
        return () => document.removeEventListener('mousedown', handler);
    }, []);

    // Close mobile menu on route change
    useEffect(() => {
        setMobileMenuOpen(false);
    }, [location.pathname]);

    const handleLockedNav = (path) => (e) => {
        if (matchId) {
            e.preventDefault();
            navigate(`/battle/${matchId}`);
        }
    };

    const linkClass = ({ isActive }) =>
        `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${isActive
            ? 'bg-accent/10 text-accent'
            : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'
        } ${matchId ? 'opacity-50 pointer-events-none' : ''}`;

    const mobileLinkClass = ({ isActive }) =>
        `flex items-center gap-3 px-4 py-3.5 rounded-xl text-base font-semibold transition-all ${isActive
            ? 'bg-accent text-white shadow-lg shadow-accent/20'
            : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'
        } ${matchId ? 'opacity-50 pointer-events-none' : ''}`;

    return (
        <nav className="sticky top-0 z-[200] bg-bg-primary/80 backdrop-blur-xl border-b border-border">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-2.5 group shrink-0">
                        <div className="w-9 h-9 rounded-lg bg-accent flex items-center justify-center">
                            <Swords size={18} className="text-white" />
                        </div>
                        <span className="text-lg font-bold text-text-primary">
                            Code<span className="text-accent">Arena</span>
                        </span>
                    </Link>

                    {/* Desktop Nav Links — hidden below md */}
                    {isAuthenticated && (
                        <div className="hidden md:flex items-center gap-1">
                            <NavLink to="/dashboard" className={linkClass} onClick={matchId ? handleLockedNav('/dashboard') : undefined}>
                                <LayoutDashboard size={16} />
                                Dashboard
                            </NavLink>
                            <NavLink to="/problems" className={linkClass} onClick={matchId ? handleLockedNav('/problems') : undefined}>
                                <Building2 size={16} />
                                Practice
                            </NavLink>
                            <NavLink to="/history" className={linkClass} onClick={matchId ? handleLockedNav('/history') : undefined}>
                                <History size={16} />
                                History
                            </NavLink>
                        </div>
                    )}

                    {/* Right Section */}
                    <div className="flex items-center gap-2 sm:gap-3">
                        {isAuthenticated ? (
                            <>
                                {/* Notifications — desktop only */}
                                <button className="hidden sm:block relative p-2 rounded-xl text-text-secondary hover:text-text-primary hover:bg-bg-hover transition-all cursor-pointer">
                                    <Bell size={18} />
                                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-accent rounded-full" />
                                </button>

                                {/* Profile Dropdown */}
                                <div className="relative" ref={dropdownRef}>
                                    <button
                                        onClick={() => setDropdownOpen(!dropdownOpen)}
                                        className={`flex items-center gap-2 py-1.5 px-1.5 sm:px-3 rounded-2xl transition-all cursor-pointer border ${dropdownOpen ? 'bg-bg-hover border-white/10 shadow-sm' : 'border-transparent hover:bg-bg-hover'}`}
                                    >
                                        <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center text-white text-sm font-bold ring-2 ring-bg-primary shrink-0">
                                            {user?.username?.charAt(0).toUpperCase()}
                                        </div>
                                        <div className="hidden sm:block text-left">
                                            <div className="text-sm font-bold text-text-primary leading-tight">{user?.username}</div>
                                            <div className="text-[11px] text-accent font-mono font-medium tracking-wide mt-0.5">{user?.elo ?? '—'} ELO</div>
                                        </div>
                                        <ChevronDown size={14} className={`text-text-muted transition-transform duration-200 hidden sm:block ${dropdownOpen ? 'rotate-180' : ''}`} />
                                    </button>

                                    <AnimatePresence>
                                        {dropdownOpen && (
                                            <motion.div
                                                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                                                className="absolute right-0 mt-2 w-56 bg-bg-secondary border border-border rounded-2xl shadow-2xl py-2 z-50 overflow-hidden"
                                            >
                                                {/* Show user info on mobile (hidden on sm+) */}
                                                <div className="px-4 py-3 border-b border-border/50 sm:hidden">
                                                    <div className="text-sm font-bold text-text-primary">{user?.username}</div>
                                                    <div className="text-xs text-accent font-mono mt-0.5">{user?.elo} ELO</div>
                                                </div>
                                                <Link to="/profile" onClick={() => setDropdownOpen(false)} className="flex items-center gap-3 px-4 py-2.5 text-sm text-text-secondary hover:text-text-primary hover:bg-bg-hover transition-colors">
                                                    <User size={16} /> Profile
                                                </Link>
                                                <Link to="/settings" onClick={() => setDropdownOpen(false)} className="flex items-center gap-3 px-4 py-2.5 text-sm text-text-secondary hover:text-text-primary hover:bg-bg-hover transition-colors">
                                                    <Settings size={16} /> Settings
                                                </Link>
                                                <div className="h-px bg-border/50 my-1" />
                                                <button
                                                    onClick={() => { setDropdownOpen(false); handleLogout(); }}
                                                    className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-loss hover:bg-loss/10 transition-colors cursor-pointer"
                                                >
                                                    <LogOut size={16} /> Logout
                                                </button>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </div>

                                {/* Mobile Menu Toggle — visible below md */}
                                <button
                                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                                    className="md:hidden p-2 rounded-xl text-text-secondary hover:text-text-primary hover:bg-bg-hover transition-all cursor-pointer"
                                >
                                    {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
                                </button>
                            </>
                        ) : (
                            <div className="flex items-center gap-3">
                                <Link to="/login" className="px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary transition-colors">
                                    Login
                                </Link>
                                <Link to="/register" className="px-4 py-2 text-sm font-semibold bg-accent hover:bg-accent-hover text-white rounded-lg transition-colors">
                                    Register
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Mobile Slide-Down Menu */}
            <AnimatePresence>
                {mobileMenuOpen && isAuthenticated && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="md:hidden bg-bg-primary border-b border-border overflow-hidden"
                    >
                        <div className="px-4 py-4 flex flex-col gap-1.5">
                            <NavLink to="/dashboard" className={mobileLinkClass} onClick={matchId ? handleLockedNav('/dashboard') : undefined}>
                                <LayoutDashboard size={20} />
                                Dashboard
                            </NavLink>
                            <NavLink to="/problems" className={mobileLinkClass} onClick={matchId ? handleLockedNav('/problems') : undefined}>
                                <Building2 size={20} />
                                Practice
                            </NavLink>
                            <NavLink to="/history" className={mobileLinkClass} onClick={matchId ? handleLockedNav('/history') : undefined}>
                                <History size={20} />
                                History
                            </NavLink>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </nav>
    );
}