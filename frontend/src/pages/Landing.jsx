import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Swords, Trophy, Shield, Terminal } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';

export default function Landing() {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: { staggerChildren: 0.15 }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 16 },
        show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } }
    };

    return (
        <div className="min-h-[calc(100vh-64px)] bg-bg-root font-sans text-text-primary">

            {/* --- MAIN CONTENT --- */}
            <div className="w-full max-w-6xl mx-auto px-6 pt-18 pb-20 flex flex-col items-center text-center">

                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="show"
                    className="paper-card grain-panel flex flex-col items-center max-w-4xl w-full px-7 py-10 sm:px-12 sm:py-14"
                >
                    <motion.p variants={itemVariants} className="editorial-kicker mb-4">
                        Built for late-night ladders and ugly wins
                    </motion.p>

                    <motion.h1 variants={itemVariants} className="text-5xl sm:text-6xl md:text-7xl font-bold tracking-[-0.05em] mb-6 leading-[0.94] max-w-3xl">
                        Competitive coding
                        <br className="hidden sm:block" />
                        with some grit.
                    </motion.h1>

                    <motion.p variants={itemVariants} className="text-lg sm:text-xl text-text-secondary leading-relaxed max-w-2xl mx-auto mb-10">
                        CodeArena should feel like a real competitive tool, not a polished startup mockup.
                        Jump into fast matches, solve under pressure, and earn every rating point.
                    </motion.p>

                    <motion.div variants={itemVariants} className="flex flex-col sm:flex-row items-center gap-4 w-full justify-center mb-10">
                        {isAuthenticated ? (
                            <Link
                                to="/dashboard"
                                className="w-full sm:w-auto px-10 py-4 bg-accent hover:bg-accent-hover text-white rounded-[18px_14px_16px_12px] border border-[#e29a6c] font-bold text-lg transition-colors flex items-center justify-center gap-3 shadow-[4px_4px_0_rgba(0,0,0,0.22)]"
                            >
                                <Terminal size={20} />
                                Enter Dashboard
                            </Link>
                        ) : (
                            <>
                                <Link
                                    to="/register"
                                    className="w-full sm:w-auto px-10 py-4 bg-accent hover:bg-accent-hover text-white rounded-[18px_14px_16px_12px] border border-[#e29a6c] font-bold text-lg transition-colors flex items-center justify-center gap-3 shadow-[4px_4px_0_rgba(0,0,0,0.22)]"
                                >
                                    <Swords size={20} />
                                    Start Competing
                                </Link>
                                <Link
                                    to="/login"
                                    className="w-full sm:w-auto px-10 py-4 bg-bg-secondary hover:bg-bg-elevated text-text-primary border border-border rounded-[18px_14px_16px_12px] font-bold text-lg transition-colors flex items-center justify-center shadow-[4px_4px_0_rgba(0,0,0,0.14)]"
                                >
                                    Log In
                                </Link>
                            </>
                        )}
                    </motion.div>

                    <motion.div variants={itemVariants} className="w-full grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
                        <div className="human-chip px-4 py-3">
                            <div className="editorial-kicker mb-1">Format</div>
                            <div className="text-sm font-medium text-text-primary">Head-to-head timed rounds</div>
                        </div>
                        <div className="human-chip px-4 py-3">
                            <div className="editorial-kicker mb-1">Rank</div>
                            <div className="text-sm font-medium text-text-primary">ELO that moves like a real ladder</div>
                        </div>
                        <div className="human-chip px-4 py-3">
                            <div className="editorial-kicker mb-1">Workflow</div>
                            <div className="text-sm font-medium text-text-primary">Code, submit, recover, repeat</div>
                        </div>
                    </motion.div>
                </motion.div>

                {/* --- FEATURES GRID --- */}
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="show"
                    className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mt-8"
                >
                    <FeatureCard
                        icon={Swords}
                        title="Head-to-Head Action"
                        description="Live WebSocket battles. See your opponent's progress and test case results in real-time."
                    />
                    <FeatureCard
                        icon={Trophy}
                        title="Chess-Style ELO"
                        description="True skill-based matchmaking. Gain massive ELO for upsetting Grandmasters."
                    />
                    <FeatureCard
                        icon={Shield}
                        title="Secure Execution"
                        description="Military-grade code isolation. Submissions run in strict Docker containers."
                    />
                </motion.div>
            </div>
        </div>
    );
}

function FeatureCard({ icon: Icon, title, description }) {
    return (
        <motion.div
            className="group paper-card-soft grain-panel flex flex-col items-center text-center p-8 transition-colors duration-200"
        >
            <div className="w-14 h-14 rounded-[16px_12px_14px_10px] bg-accent/12 border border-accent/30 flex items-center justify-center mb-5 shadow-[3px_3px_0_rgba(0,0,0,0.16)]">
                <Icon size={26} className="text-accent" />
            </div>
            <h3 className="text-xl font-bold tracking-[-0.03em] text-text-primary mb-3">{title}</h3>
            <p className="text-text-secondary text-sm leading-relaxed">{description}</p>
        </motion.div>
    );
}
