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
            <div className="w-full max-w-5xl mx-auto px-6 pt-28 pb-20 flex flex-col items-center text-center">

                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="show"
                    className="flex flex-col items-center max-w-3xl"
                >
                    <motion.h1 variants={itemVariants} className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight mb-6 leading-tight">
                        Real-Time 1v1 <br className="hidden sm:block" />
                        <span className="text-accent">Code Battles</span>
                    </motion.h1>

                    <motion.p variants={itemVariants} className="text-lg sm:text-xl text-text-secondary leading-relaxed max-w-2xl mx-auto mb-12">
                        Experience the adrenaline of blitz chess combined with competitive programming.
                        Match up instantly, outcode your opponent, and climb the global ELO leaderboard.
                    </motion.p>

                    <motion.div variants={itemVariants} className="flex flex-col sm:flex-row items-center gap-4 w-full justify-center mb-20">
                        {isAuthenticated ? (
                            <Link
                                to="/dashboard"
                                className="w-full sm:w-auto px-10 py-4 bg-accent hover:bg-accent-hover text-white rounded-lg font-bold text-lg transition-colors flex items-center justify-center gap-3"
                            >
                                <Terminal size={20} />
                                Enter Dashboard
                            </Link>
                        ) : (
                            <>
                                <Link
                                    to="/register"
                                    className="w-full sm:w-auto px-10 py-4 bg-accent hover:bg-accent-hover text-white rounded-lg font-bold text-lg transition-colors flex items-center justify-center gap-3"
                                >
                                    <Swords size={20} />
                                    Start Competing
                                </Link>
                                <Link
                                    to="/login"
                                    className="w-full sm:w-auto px-10 py-4 bg-bg-secondary hover:bg-bg-elevated text-text-primary border border-border rounded-lg font-bold text-lg transition-colors flex items-center justify-center"
                                >
                                    Log In
                                </Link>
                            </>
                        )}
                    </motion.div>
                </motion.div>

                {/* --- FEATURES GRID --- */}
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="show"
                    className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mb-12"
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
            className="group flex flex-col items-center text-center p-8 rounded-xl bg-bg-secondary border border-border hover:border-accent/40 hover:bg-bg-elevated transition-colors duration-200"
        >
            <div className="w-14 h-14 rounded-xl bg-accent/10 border border-accent/20 flex items-center justify-center mb-5">
                <Icon size={26} className="text-accent" />
            </div>
            <h3 className="text-xl font-bold text-text-primary mb-3">{title}</h3>
            <p className="text-text-secondary text-sm leading-relaxed">{description}</p>
        </motion.div>
    );
}