import { useState, useRef, useEffect } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Swords, LayoutDashboard, History, User, Bell, Settings, LogOut, ChevronDown,
} from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { useBattleStore } from '../../stores/battleStore';
import { useLogout } from '../../hooks/useAuth';

export default function Navbar() {
    const { user, isAuthenticated } = useAuthStore();
    const matchId = useBattleStore((s) => s.matchId);
    const handleLogout = useLogout();
    const navigate = useNavigate();
    const [dropdownOpen, setDropdownOpen] = useState(false);
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

    const handleLockedNav = (path) => (e) => {
        if (matchId) {
            e.preventDefault();
            navigate(`/battle/${matchId}`);
        }
    };

    const linkClass = ({ isActive }) =>
        `flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${isActive
            ? 'bg-accent/15 text-accent shadow-sm shadow-accent-glow/20'
            : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'
        } ${matchId ? 'opacity-50 pointer-events-none' : ''}`;

    return (
        <nav className="sticky top-0 z-[200] bg-bg-primary/80 backdrop-blur-xl border-b border-border">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-2.5 group">
                        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent to-accent-secondary flex items-center justify-center shadow-lg shadow-accent-glow/30 group-hover:shadow-accent-glow/50 transition-shadow">
                            <Swords size={18} className="text-white" />
                        </div>
                        <span className="text-lg font-bold text-text-primary">
                            Code<span className="text-accent">Arena</span>
                        </span>
                    </Link>

                    {/* Nav Links */}
                    {isAuthenticated && (
                        <div className="hidden sm:flex items-center gap-1">
                            <NavLink to="/dashboard" className={linkClass} onClick={matchId ? handleLockedNav('/dashboard') : undefined}>
                                <LayoutDashboard size={16} />
                                Dashboard
                            </NavLink>
                            <NavLink to="/history" className={linkClass} onClick={matchId ? handleLockedNav('/history') : undefined}>
                                <History size={16} />
                                History
                            </NavLink>
                        </div>
                    )}

                    {/* Right Section */}
                    <div className="flex items-center gap-3">
                        {isAuthenticated ? (
                            <>
                                {/* Notifications */}
                                <button className="relative p-2 rounded-xl text-text-secondary hover:text-text-primary hover:bg-bg-hover transition-all cursor-pointer">
                                    <Bell size={18} />
                                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-accent rounded-full" />
                                </button>

                                {/* Profile Dropdown */}
                                <div className="relative" ref={dropdownRef}>
                                    <button
                                        onClick={() => setDropdownOpen(!dropdownOpen)}
                                        className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl hover:bg-bg-hover transition-all cursor-pointer"
                                    >
                                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-accent to-accent-secondary flex items-center justify-center text-white text-sm font-bold">
                                            {user?.username?.charAt(0).toUpperCase()}
                                        </div>
                                        <div className="hidden sm:block text-left">
                                            <div className="text-sm font-medium text-text-primary">{user?.username}</div>
                                            <div className="text-xs text-accent font-mono">{user?.elo ?? '—'} ELO</div>
                                        </div>
                                        <ChevronDown
                                            size={14}
                                            className={`text-text-muted transition-transform duration-200 ${dropdownOpen ? 'rotate-180' : ''}`}
                                        />
                                    </button>

                                    <AnimatePresence>
                                        {dropdownOpen && (
                                            <motion.div
                                                initial={{ opacity: 0, y: -8, scale: 0.96 }}
                                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                                exit={{ opacity: 0, y: -8, scale: 0.96 }}
                                                transition={{ duration: 0.15 }}
                                                className="absolute right-0 mt-2 w-56 bg-bg-elevated border border-border rounded-xl shadow-2xl overflow-hidden"
                                            >
                                                <div className="px-4 py-3 border-b border-border">
                                                    <p className="text-sm font-semibold text-text-primary">{user?.username}</p>
                                                    <p className="text-xs text-text-secondary">{user?.email}</p>
                                                </div>

                                                <div className="py-1">
                                                    <DropdownItem icon={User} label="Profile" onClick={() => { setDropdownOpen(false); navigate('/profile'); }} />
                                                    <DropdownItem icon={Settings} label="Settings" onClick={() => { setDropdownOpen(false); navigate('/settings'); }} />
                                                </div>

                                                <div className="border-t border-border py-1">
                                                    <DropdownItem
                                                        icon={LogOut}
                                                        label="Logout"
                                                        danger
                                                        onClick={() => { setDropdownOpen(false); handleLogout(); }}
                                                    />
                                                </div>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </div>
                            </>
                        ) : (
                            <div className="flex items-center gap-2">
                                <Link
                                    to="/login"
                                    className="px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary transition-colors"
                                >
                                    Login
                                </Link>
                                <Link
                                    to="/register"
                                    className="px-4 py-2 text-sm font-semibold bg-accent hover:bg-accent-hover text-white rounded-xl transition-colors shadow-lg shadow-accent-glow/30"
                                >
                                    Register
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}

function DropdownItem({ icon: Icon, label, danger = false, onClick }) {
    return (
        <button
            onClick={onClick}
            className={`
        w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors cursor-pointer
        ${danger
                    ? 'text-loss hover:bg-loss/10'
                    : 'text-text-secondary hover:bg-bg-hover hover:text-text-primary'
                }
      `}
        >
            <Icon size={16} />
            {label}
        </button>
    );
}
