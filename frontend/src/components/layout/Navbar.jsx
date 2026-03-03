import { useState, useRef, useEffect } from 'react';
import { Link, NavLink, useNavigate, useLocation } from 'react-router-dom';
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
    const location = useLocation();
    const isOnLogin = location.pathname === '/login';
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
        `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${isActive
            ? 'bg-accent/10 text-accent'
            : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'
        } ${matchId ? 'opacity-50 pointer-events-none' : ''}`;

    return (
        <nav className="sticky top-0 z-[200] bg-bg-primary/80 backdrop-blur-xl border-b border-border">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-2.5 group">
                        <div className="w-9 h-9 rounded-lg bg-accent flex items-center justify-center">
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
                                        className={`flex items-center gap-2.5 px-3 py-1.5 rounded-2xl transition-all cursor-pointer border ${dropdownOpen ? 'bg-bg-hover border-white/10 shadow-sm' : 'border-transparent hover:bg-bg-hover'}`}
                                    >
                                        <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center text-white text-sm font-bold ring-2 ring-bg-primary">
                                            {user?.username?.charAt(0).toUpperCase()}
                                        </div>
                                        <div className="hidden sm:block text-left">
                                            <div className="text-sm font-bold text-text-primary leading-tight">{user?.username}</div>
                                            <div className="text-[11px] text-accent font-mono font-medium tracking-wide mt-0.5">{user?.elo ?? '—'} ELO</div>
                                        </div>
                                        <ChevronDown
                                            size={14}
                                            className={`text-text-muted transition-transform duration-200 ml-1 ${dropdownOpen ? 'rotate-180 text-text-primary' : ''}`}
                                        />
                                    </button>

                                    <AnimatePresence>
                                        {dropdownOpen && (
                                            <motion.div
                                                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                                                transition={{ duration: 0.15, ease: "easeOut" }}
                                                // Changed width to w-80 for a bigger card
                                                className="absolute right-0 mt-3 w-80 bg-bg-elevated border border-border rounded-xl shadow-xl overflow-hidden"
                                            >
                                                {/* User Info Header - Increased padding and gap */}
                                                <div className="p-6 border-b border-border flex items-center gap-5">
                                                    <div className="relative shrink-0">
                                                        {/* Increased Avatar Size */}
                                                        <div className="w-14 h-14 rounded-full bg-accent flex items-center justify-center text-white font-bold text-2xl">
                                                            {user?.username?.charAt(0).toUpperCase()}
                                                        </div>
                                                        {/* Increased Online Status Indicator */}
                                                        <div className="absolute bottom-0 right-0 w-4 h-4 bg-green-500 border-[2.5px] border-bg-elevated rounded-full"></div>
                                                    </div>

                                                    <div className="flex-1 overflow-hidden">
                                                        {/* Increased font sizes slightly for the header */}
                                                        <p className="text-lg font-bold text-text-primary truncate">{user?.username}</p>
                                                        <p className="text-sm text-text-muted truncate mt-0.5">{user?.email}</p>

                                                        {/* ELO Badge */}
                                                        <div className="mt-2.5 inline-flex items-center px-2.5 py-1 rounded-md text-[11px] font-mono font-bold bg-accent/10 text-accent border border-accent/20 tracking-wide">
                                                            🏆 {user?.elo ?? '—'} ELO
                                                        </div>
                                                    </div>
                                                </div>

                                                {/* Actions - Increased padding */}
                                                <div className="p-3 space-y-1.5">
                                                    <DropdownItem
                                                        icon={User}
                                                        label="Profile"
                                                        onClick={() => { setDropdownOpen(false); navigate('/profile'); }}
                                                    />
                                                    <DropdownItem
                                                        icon={Settings}
                                                        label="Settings"
                                                        onClick={() => { setDropdownOpen(false); navigate('/settings'); }}
                                                    />
                                                </div>

                                                {/* Logout Section */}
                                                <div className="p-3 border-t border-border">
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
                            <div className="flex items-center gap-4">
                                <Link
                                    to="/login"
                                    className={isOnLogin
                                        ? "px-4 py-2 text-sm font-semibold bg-accent hover:bg-accent-hover text-white rounded-lg transition-colors"
                                        : "px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary transition-colors"
                                    }
                                >
                                    Login
                                </Link>
                                <Link
                                    to="/register"
                                    className={!isOnLogin
                                        ? "px-4 py-2 text-sm font-semibold bg-accent hover:bg-accent-hover text-white rounded-lg transition-colors"
                                        : "px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary transition-colors"
                                    }
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
                group w-full flex items-center gap-4 px-4 py-3.5 rounded-xl text-base font-medium transition-all duration-200 cursor-pointer
                ${danger
                    ? 'text-red-400 hover:bg-red-500/10 hover:text-red-300'
                    : 'text-text-secondary hover:bg-white/10 hover:text-text-primary'
                }
            `}
        >
            <div className={`
                p-2.5 rounded-xl transition-all duration-200 flex items-center justify-center
                ${danger
                    ? 'bg-red-500/10 group-hover:bg-red-500/20 group-hover:scale-105'
                    : 'bg-white/5 group-hover:bg-white/10 group-hover:text-accent group-hover:scale-105'
                }
            `}>
                <Icon size={18} />
            </div>
            {label}
        </button>
    );
}