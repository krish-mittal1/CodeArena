import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Swords, Trophy, Shield, Terminal, Zap, Code2 } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';

export default function Landing() {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: { staggerChildren: 0.2 }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } }
    };

    return (
        <div className="relative min-h-[calc(100vh-64px)] bg-[#09090b] overflow-hidden font-sans text-white">

            {/* --- BACKGROUND EFFECTS --- */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:32px_32px]" />

            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center justify-center opacity-[0.03] pointer-events-none select-none">
                <Code2 size={400} />
                <h1 className="text-[10rem] font-black tracking-tighter mt-4">CodeArena</h1>
            </div>

            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-purple-600/20 rounded-full blur-[150px] pointer-events-none" />
            <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none" />

            {/* --- MAIN CONTENT --- */}
            <div className="relative z-10 w-full max-w-6xl mx-auto px-6 pt-28 pb-20 flex flex-col items-center text-center">

                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="show"
                    className="flex flex-col items-center max-w-3xl"
                >
                    <motion.h1 variants={itemVariants} className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight mb-6 leading-tight">
                        Real-Time 1v1 <br className="hidden sm:block" />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-indigo-400 to-purple-400 animate-gradient-x">
                            Code Battles
                        </span>
                    </motion.h1>

                    <motion.p variants={itemVariants} className="text-lg sm:text-xl text-zinc-400 leading-relaxed max-w-2xl mx-auto mb-12">
                        Experience the adrenaline of blitz chess combined with competitive programming.
                        Match up instantly, outcode your opponent, and climb the global ELO leaderboard.
                    </motion.p>

                    <motion.div variants={itemVariants} className="flex flex-col sm:flex-row items-center gap-5 w-full justify-center mb-20">
                        {isAuthenticated ? (
                            <Link
                                to="/dashboard"
                                className="w-full sm:w-auto px-10 py-4 bg-purple-600 hover:bg-purple-500 text-white rounded-xl font-bold text-lg shadow-[0_0_30px_rgba(168,85,247,0.3)] hover:shadow-[0_0_40px_rgba(168,85,247,0.5)] transition-all flex items-center justify-center gap-3"
                            >
                                <Terminal size={20} />
                                Enter Dashboard
                            </Link>
                        ) : (
                            <>
                                <Link
                                    to="/register"
                                    className="w-full sm:w-auto px-10 py-4 bg-purple-600 hover:bg-purple-500 text-white rounded-xl font-bold text-lg shadow-[0_0_30px_rgba(168,85,247,0.3)] hover:shadow-[0_0_40px_rgba(168,85,247,0.5)] transition-all flex items-center justify-center gap-3"
                                >
                                    <Swords size={20} />
                                    Start Competing
                                </Link>
                                <Link
                                    to="/login"
                                    className="w-full sm:w-auto px-10 py-4 bg-[#121217] hover:bg-[#1a1a24] text-white border border-white/10 rounded-xl font-bold text-lg transition-all flex items-center justify-center"
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
                    className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full mb-12"
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
            className="group flex flex-col items-center text-center p-10 rounded-3xl bg-[#121217] border border-white/5 hover:border-purple-500/30 hover:bg-[#16161c] transition-all duration-300 relative overflow-hidden"
        >
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-1 bg-purple-500/0 group-hover:bg-purple-500/50 blur-[8px] transition-all duration-500" />
            <div className="w-16 h-16 rounded-2xl bg-[#09090b] border border-white/10 flex items-center justify-center mb-6 group-hover:scale-110 group-hover:bg-purple-500/10 transition-all duration-300">
                <Icon size={30} className="text-zinc-500 group-hover:text-purple-400 transition-colors" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-4 tracking-wide">{title}</h3>
            <p className="text-zinc-400 text-base leading-relaxed">{description}</p>
        </motion.div>
    );
}