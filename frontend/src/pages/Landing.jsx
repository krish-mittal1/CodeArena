import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    ArrowRight,
    Bot,
    BrainCircuit,
    Building2,
    FileClock,
    Shield,
    Swords,
    TerminalSquare,
    Trophy,
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';

const heroLogLines = [
    '[BOOT] Arena runtime online',
    '[QUEUE] Live matchmaking + private rooms ready',
    '[PRACTICE] Company-wise DSA and CP tracks loaded',
    '[JUDGE] Docker-backed execution runners active',
    '[ANALYSIS] AI review available after DSA submissions',
];

const systemStrip = [
    { label: 'Match Format', value: '1v1 battles + practice tracks' },
    { label: 'Judge Mode', value: 'Hidden tests + sample runs' },
    { label: 'Progress Layer', value: 'ELO, history, solved state' },
    { label: 'Problem Modes', value: 'LeetCode-style and Codeforces-style' },
];

const featureBlocks = [
    {
        eyebrow: 'Live arena',
        title: 'Head-to-head battles that actually feel competitive.',
        description:
            'Queue into real-time matches, submit under a timer, and track the result through live WebSocket events instead of fake static screens.',
        icon: Swords,
        span: 'md:col-span-2',
    },
    {
        eyebrow: 'Rating system',
        title: 'ELO that moves with every real result.',
        description:
            'Wins, losses, and match history feed a proper rating loop so the dashboard reflects your actual trajectory.',
        icon: Trophy,
        span: 'md:col-span-1',
    },
    {
        eyebrow: 'Practice stack',
        title: 'Two tracks, two workflows.',
        description:
            'Use company-wise DSA practice with AI analysis, or switch into competitive programming mode with raw stdin/stdout and rating-based problems.',
        icon: Building2,
        span: 'md:col-span-1',
    },
    {
        eyebrow: 'AI support',
        title: 'Analysis where it helps, not where it distracts.',
        description:
            'After DSA submissions, CodeArena can explain verdicts, failed tests, and better approaches without turning every page into AI clutter.',
        icon: BrainCircuit,
        span: 'md:col-span-1',
    },
    {
        eyebrow: 'Execution',
        title: 'Container-backed judging for actual code runs.',
        description:
            'Submissions are executed through isolated runners so practice and battle verdicts come from the judge, not mocked frontend logic.',
        icon: Shield,
        span: 'md:col-span-1',
    },
    {
        eyebrow: 'History',
        title: 'Past attempts stay visible.',
        description:
            'Accepted submissions mark problems as solved, match history stays accessible, and your earlier attempts remain part of the record.',
        icon: FileClock,
        span: 'md:col-span-2',
    },
];

export default function Landing() {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

    return (
        <div className="min-h-[calc(100vh-64px)] bg-[#120c08] text-[#f3e7da] overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(201,109,58,0.16),transparent_38%),linear-gradient(180deg,rgba(36,21,14,0.96),rgba(18,12,8,1))]" />
            <div className="absolute inset-x-0 top-0 h-[520px] opacity-20 [background-image:linear-gradient(rgba(255,255,255,0.06)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.06)_1px,transparent_1px)] [background-size:28px_28px]" />
            <div className="absolute inset-x-0 bottom-0 h-[420px] bg-[linear-gradient(180deg,transparent,rgba(201,109,58,0.06))]" />

            <div className="relative max-w-7xl mx-auto px-6 sm:px-8 pb-24">
                <section className="pt-14 sm:pt-18">
                    <div className="grid gap-10 lg:grid-cols-[minmax(0,1.1fr)_420px] lg:items-center">
                        <motion.div
                            initial={{ opacity: 0, y: 18 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, ease: 'easeOut' }}
                            className="max-w-3xl"
                        >
                            <div className="inline-flex items-center gap-3 border border-[#5d4435] bg-[#251911]/80 px-4 py-2 text-[11px] uppercase tracking-[0.28em] text-[#f0b18a] shadow-[0_0_0_1px_rgba(255,255,255,0.03)]">
                                <span className="h-3 w-1 bg-[#f0a06f]" />
                                <span>System status: operational</span>
                            </div>

                            <h1 className="mt-8 text-[3.2rem] leading-[0.92] sm:text-[4.9rem] lg:text-[5.8rem] font-black tracking-[-0.06em] uppercase">
                                <span className="block text-[#f6eadf] drop-shadow-[0_2px_0_rgba(0,0,0,0.45)]">
                                    Competitive coding
                                </span>
                                <span className="block text-[#f0a06f] drop-shadow-[0_2px_0_rgba(0,0,0,0.45)]">
                                    with real pressure.
                                </span>
                            </h1>

                            <p className="mt-8 max-w-2xl text-lg sm:text-xl leading-relaxed text-[#dbc4b3]">
                                CodeArena combines live coding battles, company-wise DSA prep, competitive programming practice,
                                isolated judging, and post-submission AI analysis into one arena. No fake metrics. No fluff features.
                            </p>

                            <div className="mt-10 flex flex-col sm:flex-row gap-4">
                                {isAuthenticated ? (
                                    <>
                                        <Link
                                            to="/dashboard"
                                            className="inline-flex items-center justify-center gap-3 bg-[#f0a06f] px-7 py-4 text-sm font-black uppercase tracking-[0.22em] text-[#1b120d] shadow-[0_10px_30px_rgba(240,160,111,0.16)] transition-transform hover:-translate-y-0.5"
                                        >
                                            <TerminalSquare size={18} />
                                            Enter dashboard
                                        </Link>
                                        <Link
                                            to="/problems"
                                            className="inline-flex items-center justify-center gap-3 border border-[#5d4435] bg-[#211610] px-7 py-4 text-sm font-bold uppercase tracking-[0.18em] text-[#f3e7da] transition-colors hover:border-[#8a6047] hover:bg-[#291b14]"
                                        >
                                            Explore practice
                                        </Link>
                                    </>
                                ) : (
                                    <>
                                        <Link
                                            to="/register"
                                            className="inline-flex items-center justify-center gap-3 bg-[#f0a06f] px-7 py-4 text-sm font-black uppercase tracking-[0.22em] text-[#1b120d] shadow-[0_10px_30px_rgba(240,160,111,0.16)] transition-transform hover:-translate-y-0.5"
                                        >
                                            <Swords size={18} />
                                            Start competing
                                        </Link>
                                        <Link
                                            to="/login"
                                            className="inline-flex items-center justify-center gap-3 border border-[#5d4435] bg-[#211610] px-7 py-4 text-sm font-bold uppercase tracking-[0.18em] text-[#f3e7da] transition-colors hover:border-[#8a6047] hover:bg-[#291b14]"
                                        >
                                            Log in
                                        </Link>
                                    </>
                                )}
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, x: 28 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.55, ease: 'easeOut', delay: 0.08 }}
                            className="relative"
                        >
                            <div className="border border-[#3d2a1f] bg-[#1a120d]/92 p-5 shadow-[0_24px_60px_rgba(0,0,0,0.28)] backdrop-blur-sm">
                                <div className="flex items-center justify-between border-b border-[#33231a] pb-3 text-[10px] uppercase tracking-[0.24em] text-[#a8846d]">
                                    <span>Runtime process</span>
                                    <span>arena.runtime</span>
                                </div>

                                <div className="mt-4 space-y-2 font-mono text-[12px] leading-6 text-[#d1b19a]">
                                    {heroLogLines.map((line) => (
                                        <div key={line} className="truncate">
                                            {line}
                                        </div>
                                    ))}
                                </div>

                                <div className="mt-8 space-y-3">
                                    <div className="h-2 bg-[#2b1d15]">
                                        <div className="h-full w-[88%] bg-[#8d654d]" />
                                    </div>
                                    <div className="h-2 bg-[#2b1d15]">
                                        <div className="h-full w-[72%] bg-[#6c4d3b]" />
                                    </div>
                                    <div className="h-2 bg-[#2b1d15]">
                                        <div className="h-full w-[64%] bg-[#8d654d]" />
                                    </div>
                                </div>

                                <div className="mt-8 flex items-start gap-3 border border-[#3c2a1f] bg-[#140e0a] px-4 py-3">
                                    <Bot size={18} className="mt-0.5 text-[#f0a06f]" />
                                    <div>
                                        <p className="text-[11px] uppercase tracking-[0.24em] text-[#9c7863]">Operational notes</p>
                                        <p className="mt-1 text-sm leading-relaxed text-[#d6b7a0]">
                                            Live queue, rating, history, DSA analysis, and CP mode are available. The page sells only features the app already has.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                </section>

                <section className="mt-12 grid grid-cols-1 divide-y divide-[#2f2017] border border-[#35251b] bg-[#1b120d]/88 sm:grid-cols-2 sm:divide-x sm:divide-y-0 xl:grid-cols-4">
                    {systemStrip.map((item, index) => (
                        <motion.div
                            key={item.label}
                            initial={{ opacity: 0, y: 14 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.12 + index * 0.05, duration: 0.4 }}
                            className="px-6 py-5"
                        >
                            <p className="text-[10px] uppercase tracking-[0.24em] text-[#9e7b66]">{item.label}</p>
                            <p className="mt-2 text-lg font-bold tracking-[-0.03em] text-[#f0a06f]">{item.value}</p>
                        </motion.div>
                    ))}
                </section>

                <section className="mt-20">
                    <motion.div
                        initial={{ opacity: 0, y: 18 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.45 }}
                    >
                        <p className="text-[11px] uppercase tracking-[0.28em] text-[#a8846d]">Forge your workflow</p>
                        <h2 className="mt-4 text-4xl sm:text-5xl font-black tracking-[-0.05em] uppercase text-[#f6eadf]">
                            Built around how the app actually works.
                        </h2>
                    </motion.div>

                    <div className="mt-10 grid gap-5 md:grid-cols-3">
                        {featureBlocks.map((block, index) => {
                            const Icon = block.icon;
                            return (
                                <motion.div
                                    key={block.title}
                                    initial={{ opacity: 0, y: 18 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.12 + index * 0.06, duration: 0.42 }}
                                    className={`${block.span} border border-[#3a281d] bg-[#1b120d]/90 p-6 sm:p-7`}
                                >
                                    <div className="flex items-center justify-between gap-4">
                                        <p className="text-[10px] uppercase tracking-[0.24em] text-[#9e7b66]">{block.eyebrow}</p>
                                        <Icon size={20} className="text-[#f0a06f]" />
                                    </div>
                                    <h3 className="mt-6 max-w-2xl text-2xl sm:text-[2rem] leading-[1.02] font-black uppercase tracking-[-0.05em] text-[#f6eadf]">
                                        {block.title}
                                    </h3>
                                    <p className="mt-5 max-w-2xl text-sm sm:text-base leading-relaxed text-[#d6b7a0]">
                                        {block.description}
                                    </p>
                                </motion.div>
                            );
                        })}
                    </div>
                </section>

                <section className="mt-20 border border-[#3a281d] bg-[linear-gradient(180deg,rgba(33,22,16,0.98),rgba(24,16,12,0.98))] px-6 py-14 text-center sm:px-10">
                    <motion.div
                        initial={{ opacity: 0, y: 16 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.45 }}
                    >
                        <p className="text-[11px] uppercase tracking-[0.28em] text-[#a8846d]">Ready state</p>
                        <h2 className="mt-4 text-4xl sm:text-5xl font-black tracking-[-0.05em] uppercase text-[#f6eadf]">
                            Enter the arena with intent.
                        </h2>
                        <p className="mx-auto mt-5 max-w-3xl text-base sm:text-lg leading-relaxed text-[#d6b7a0]">
                            Practice interview problems, switch to Codeforces-style CP, review AI explanations, or queue into a live match.
                            Everything here points back to those actual workflows.
                        </p>

                        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                            <Link
                                to={isAuthenticated ? '/problems' : '/register'}
                                className="inline-flex items-center justify-center gap-3 bg-[#f0a06f] px-8 py-4 text-sm font-black uppercase tracking-[0.22em] text-[#1b120d] shadow-[0_14px_34px_rgba(240,160,111,0.14)] transition-transform hover:-translate-y-0.5"
                            >
                                {isAuthenticated ? 'Open practice' : 'Create account'}
                                <ArrowRight size={18} />
                            </Link>
                            {!isAuthenticated && (
                                <Link
                                    to="/login"
                                    className="inline-flex items-center justify-center gap-3 border border-[#5d4435] bg-[#211610] px-8 py-4 text-sm font-bold uppercase tracking-[0.18em] text-[#f3e7da] transition-colors hover:border-[#8a6047] hover:bg-[#291b14]"
                                >
                                    Log in
                                </Link>
                            )}
                        </div>
                    </motion.div>
                </section>
            </div>
        </div>
    );
}
