import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    ArrowRight, Building2, Cpu, Sparkles, Trophy,
} from 'lucide-react';

export default function Problems() {
    const navigate = useNavigate();
    const tracks = useMemo(() => ([
        {
            key: 'dsa',
            title: 'Company-wise DSA',
            subtitle: 'Interview-style LeetCode practice with AI analysis',
            description: 'Practice by company, topic, and difficulty with function-signature problems, hidden tests, and AI explanations after submissions.',
            icon: Building2,
            accent: 'from-[#d57b49]/20 via-[#d57b49]/8 to-transparent',
            border: 'border-[#d57b49]/30',
            points: ['Company mapped', 'AI analysis', 'LeetCode-style editor'],
            action: () => navigate('/practice/dsa'),
            cta: 'Open DSA track',
        },
        {
            key: 'cp',
            title: 'Competitive Programming',
            subtitle: 'Codeforces-style stdin/stdout practice by rating',
            description: 'Write full solutions from scratch using raw input and output. Problems are grouped by ratings like 800 and 900, just like a real CP ladder.',
            icon: Trophy,
            accent: 'from-[#7ec4cf]/20 via-[#7ec4cf]/8 to-transparent',
            border: 'border-[#7ec4cf]/30',
            points: ['Rating-based', 'Raw stdin/stdout', 'Codeforces-style judging'],
            action: () => navigate('/practice/competitive'),
            cta: 'Open CP track',
        },
    ]), [navigate]);

    return (
        <div className="min-h-screen bg-bg-root pb-20">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
                    <div className="flex items-center gap-3 mb-1">
                        <div className="w-10 h-10 rounded-[14px_11px_13px_9px] bg-accent/10 flex items-center justify-center shadow-[2px_2px_0_rgba(0,0,0,0.14)]">
                            <Cpu size={20} className="text-accent" />
                        </div>
                        <div>
                            <p className="editorial-kicker mb-2">Practice</p>
                            <h1 className="text-2xl sm:text-3xl font-bold text-text-primary tracking-[-0.05em]">
                                Choose your arena
                            </h1>
                            <p className="text-text-secondary text-sm">
                                Pick structured DSA prep or full competitive programming mode
                            </p>
                        </div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="mt-6 paper-card-soft p-5 sm:p-6"
                >
                    <div className="flex items-start gap-3">
                        <Sparkles size={18} className="text-accent mt-0.5" />
                        <div>
                            <p className="text-sm font-semibold text-text-primary">Two focused practice modes</p>
                            <p className="text-sm text-text-secondary leading-relaxed mt-1">
                                DSA keeps the interview-style method-signature workflow and AI guidance. Competitive programming gives you
                                full stdin/stdout coding with rating-based problems and Codeforces-like judging.
                            </p>
                        </div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="mt-8 grid grid-cols-1 xl:grid-cols-2 gap-5"
                >
                    {tracks.map((track, idx) => {
                        const Icon = track.icon;
                        return (
                            <motion.button
                                key={track.key}
                                initial={{ opacity: 0, y: 15 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.15 + idx * 0.08 }}
                                onClick={track.action}
                                className={`group text-left paper-card-soft overflow-hidden p-0 transition-all duration-300 hover:-translate-y-1 hover:border-border-hover ${track.border}`}
                            >
                                <div className={`h-full bg-gradient-to-br ${track.accent}`}>
                                    <div className="p-6 sm:p-7">
                                        <div className="flex items-start justify-between gap-4">
                                            <div className="w-12 h-12 rounded-[16px_12px_14px_10px] bg-bg-primary/70 border border-border flex items-center justify-center shadow-[2px_2px_0_rgba(0,0,0,0.12)]">
                                                <Icon size={22} className="text-accent" />
                                            </div>
                                            <ArrowRight size={18} className="text-text-muted transition-all group-hover:text-accent group-hover:translate-x-1" />
                                        </div>

                                        <div className="mt-6">
                                            <p className="editorial-kicker mb-2">{track.subtitle}</p>
                                            <h2 className="text-2xl font-bold text-text-primary tracking-[-0.04em]">
                                                {track.title}
                                            </h2>
                                            <p className="mt-3 text-sm text-text-secondary leading-relaxed">
                                                {track.description}
                                            </p>
                                        </div>

                                        <div className="mt-5 flex flex-wrap gap-2">
                                            {track.points.map((point) => (
                                                <span
                                                    key={point}
                                                    className="px-3 py-1.5 rounded-full border border-border bg-bg-primary/60 text-xs font-semibold text-text-secondary"
                                                >
                                                    {point}
                                                </span>
                                            ))}
                                        </div>

                                        <div className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-accent">
                                            {track.cta}
                                            <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
                                        </div>
                                    </div>
                                </div>
                            </motion.button>
                        );
                    })}
                </motion.div>
            </div>
        </div>
    );
}
