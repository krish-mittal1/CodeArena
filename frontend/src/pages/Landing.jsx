import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Swords, Trophy, Shield, Terminal, Zap, Code2 } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';

export default function Landing() {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

    const containerVariants = {
        hidden: { opacity: 0 },
        show: { opacity: 1, transition: { staggerChildren: 0.15 } }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 30 },
        show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } }
    };

    return (
        <div className="relative min-h-screen bg-[#09090b] overflow-x-hidden flex flex-col items-center font-sans text-white">
            {/* Background Grids & Glows */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:40px_40px]" />
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-purple-600/20 rounded-full blur-[160px] pointer-events-none" />

            <div className="relative z-10 w-full max-w-7xl mx-auto px-6 pt-32 pb-40 flex flex-col items-center">
                {/* Hero Section */}
                <motion.div 
                    variants={containerVariants}
                    initial="hidden"
                    animate="show"
                    className="flex flex-col items-center text-center mb-40" // Forced Spacing
                >
                    <motion.div variants={itemVariants} className="flex items-center gap-2 px-5 py-2 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 font-bold text-xs uppercase tracking-widest mb-10">
                        <Zap size={14} className="fill-purple-500" />
                        <span>Season 1 is now live</span>
                    </motion.div>

                    <motion.h1 variants={itemVariants} className="text-6xl md:text-8xl font-black tracking-tighter mb-8 leading-none">
                        Real-Time 1v1 <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-violet-400 to-indigo-400">
                            Code Battles
                        </span>
                    </motion.h1>

                    <motion.p variants={itemVariants} className="text-xl text-zinc-400 leading-relaxed max-w-2xl mx-auto mb-16">
                        Outcode your opponent in high-stakes blitz programming. 
                        Climb the global ELO leaderboard and prove your dominance.
                    </motion.p>

                    <motion.div variants={itemVariants} className="flex flex-col sm:flex-row items-center gap-6">
                        {isAuthenticated ? (
                            <Link to="/dashboard" className="group px-10 py-5 bg-purple-600 hover:bg-purple-500 text-white rounded-2xl font-bold text-xl shadow-[0_0_50px_rgba(168,85,247,0.4)] transition-all flex items-center gap-3">
                                <Terminal size={24} className="group-hover:rotate-12 transition-transform" />
                                Enter Dashboard
                            </Link>
                        ) : (
                            <Link to="/register" className="px-10 py-5 bg-purple-600 hover:bg-purple-500 text-white rounded-2xl font-bold text-xl shadow-[0_0_50px_rgba(168,85,247,0.4)] transition-all flex items-center gap-3">
                                <Swords size={24} /> Start Competing
                            </Link>
                        )}
                    </motion.div>
                </motion.div>

                {/* Features Grid */}
                <motion.div 
                    variants={containerVariants}
                    initial="hidden"
                    whileInView="show"
                    viewport={{ once: true }}
                    className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full"
                >
                    <FeatureCard icon={Swords} title="Head-to-Head" description="Real-time WebSocket sync. See every keystroke and test result as it happens." />
                    <FeatureCard icon={Trophy} title="Competitive ELO" description="Ranked matchmaking inspired by Grandmaster chess systems." />
                    <FeatureCard icon={Shield} title="Secure Sandbox" description="Isolated Docker execution environments for every single submission." />
                </motion.div>
            </div>
        </div>
    );
}

function FeatureCard({ icon: Icon, title, description }) {
    return (
        <motion.div className="p-10 rounded-3xl bg-[#121217]/50 border border-white/5 hover:border-purple-500/40 hover:bg-[#16161c] transition-all duration-500 group">
            <div className="w-14 h-14 rounded-xl bg-purple-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Icon size={28} className="text-purple-400" />
            </div>
            <h3 className="text-2xl font-bold mb-4">{title}</h3>
            <p className="text-zinc-400 leading-relaxed">{description}</p>
        </motion.div>
    );
}