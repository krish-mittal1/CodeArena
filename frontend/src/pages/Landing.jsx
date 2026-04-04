import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    ArrowRight, BarChart3, BrainCircuit, Building2,
    Code2, Shield, Swords, Terminal,
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';

const heroLogLines = [
    '[BOOT] Arena systems online',
    '[QUEUE] Matchmaking ready — find opponents in seconds',
    '[DSA] Company problems loaded — Google, Amazon, Meta...',
    '[CP] Competitive problems active — rated 800 to 2000+',
    '[JUDGE] Docker execution runners active',
];

const platformInfo = [
    { label: 'Match Format', value: '1v1 Real-time Battles' },
    { label: 'Practice Tracks', value: 'Company DSA + Competitive' },
    { label: 'Code Execution', value: 'Docker-isolated Judging' },
    { label: 'Progress', value: 'ELO Rating + Match History' },
];

export default function Landing() {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

    return (
        <div className="min-h-[calc(100vh-64px)] bg-[#120c08] text-[#f3e7da] overflow-hidden">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(201,109,58,0.16),transparent_38%),linear-gradient(180deg,rgba(36,21,14,0.96),rgba(18,12,8,1))]" />
            <div className="absolute inset-x-0 top-0 h-[520px] opacity-20 [background-image:linear-gradient(rgba(255,255,255,0.06)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.06)_1px,transparent_1px)] [background-size:28px_28px]" />
            <div className="absolute inset-x-0 bottom-0 h-[420px] bg-[linear-gradient(180deg,transparent,rgba(201,109,58,0.06))]" />

            <div className="relative max-w-7xl mx-auto px-6 sm:px-8 pb-24">

                {/* ═══ HERO ═══ */}
                <section className="pt-14 sm:pt-18">
                    <div className="grid gap-10 lg:grid-cols-[minmax(0,1.1fr)_420px] lg:items-center">
                        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, ease: 'easeOut' }} className="max-w-3xl">
                            <div className="inline-flex items-center gap-3 border border-[#5d4435] bg-[#251911]/80 px-4 py-2 text-[11px] uppercase tracking-[0.28em] text-[#f0b18a] shadow-[0_0_0_1px_rgba(255,255,255,0.03)]">
                                <span className="h-3 w-1 bg-[#f0a06f]" />
                                <span>System status: operational // Arena v2.4</span>
                            </div>

                            <h1 className="mt-8 text-[3.2rem] leading-[0.92] sm:text-[4.9rem] lg:text-[5.8rem] font-black tracking-[-0.06em] uppercase">
                                <span className="block text-[#f6eadf] drop-shadow-[0_2px_0_rgba(0,0,0,0.45)]">Competitive coding</span>
                                <span className="block text-[#f0a06f] drop-shadow-[0_2px_0_rgba(0,0,0,0.45)]">with some grit.</span>
                            </h1>

                            <p className="mt-8 max-w-2xl text-lg sm:text-xl leading-relaxed text-[#dbc4b3]">
                                CodeArena is built for real practice. Battle other coders 1v1, solve company interview problems, or grind competitive programming — all with proper judging and your own ELO rating.
                            </p>

                            <div className="mt-10 flex flex-col sm:flex-row gap-4">
                                {isAuthenticated ? (
                                    <>
                                        <Link to="/dashboard" className="inline-flex items-center justify-center gap-3 bg-[#f0a06f] px-7 py-4 text-sm font-black uppercase tracking-[0.22em] text-[#1b120d] shadow-[0_10px_30px_rgba(240,160,111,0.16)] transition-transform hover:-translate-y-0.5">
                                            <Terminal size={18} /> Enter dashboard
                                        </Link>
                                        <Link to="/problems" className="inline-flex items-center justify-center gap-3 border border-[#5d4435] bg-[#211610] px-7 py-4 text-sm font-bold uppercase tracking-[0.18em] text-[#f3e7da] transition-colors hover:border-[#8a6047] hover:bg-[#291b14]">
                                            Explore practice
                                        </Link>
                                    </>
                                ) : (
                                    <>
                                        <Link to="/register" className="inline-flex items-center justify-center gap-3 bg-[#f0a06f] px-7 py-4 text-sm font-black uppercase tracking-[0.22em] text-[#1b120d] shadow-[0_10px_30px_rgba(240,160,111,0.16)] transition-transform hover:-translate-y-0.5">
                                            <Swords size={18} /> Start competing
                                        </Link>
                                        <Link to="/login" className="inline-flex items-center justify-center gap-3 border border-[#5d4435] bg-[#211610] px-7 py-4 text-sm font-bold uppercase tracking-[0.18em] text-[#f3e7da] transition-colors hover:border-[#8a6047] hover:bg-[#291b14]">
                                            Log in
                                        </Link>
                                    </>
                                )}
                            </div>
                        </motion.div>

                        {/* Terminal panel */}
                        <motion.div initial={{ opacity: 0, x: 28 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.55, ease: 'easeOut', delay: 0.08 }} className="relative">
                            <div className="border border-[#3d2a1f] bg-[#1a120d]/92 p-5 shadow-[0_24px_60px_rgba(0,0,0,0.28)] backdrop-blur-sm">
                                <div className="flex items-center justify-between border-b border-[#33231a] pb-3 text-[10px] uppercase tracking-[0.24em] text-[#a8846d]">
                                    <span>Runtime process</span>
                                    <span>arena.runtime v1.0</span>
                                </div>
                                <div className="mt-4 space-y-2 font-mono text-[12px] leading-6 text-[#d1b19a]">
                                    {heroLogLines.map((line, i) => (
                                        <motion.div key={line} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 + i * 0.12, duration: 0.3 }} className="truncate">
                                            {line}
                                        </motion.div>
                                    ))}
                                </div>
                                <div className="mt-8 space-y-3">
                                    <div className="flex items-center justify-between text-[10px] uppercase tracking-[0.2em] text-[#9c7863]">
                                        <span>Match_queue</span>
                                        <span className="text-[#f0a06f]">active</span>
                                    </div>
                                    {[88, 72, 64].map((w, i) => (
                                        <div key={i} className="h-2 bg-[#2b1d15]">
                                            <motion.div className={`h-full ${i === 1 ? 'bg-[#6c4d3b]' : 'bg-[#8d654d]'}`} initial={{ width: 0 }} animate={{ width: `${w}%` }} transition={{ delay: 0.6 + i * 0.1, duration: 0.8, ease: 'easeOut' }} />
                                        </div>
                                    ))}
                                </div>
                                <div className="mt-8 flex items-center justify-between border-t border-[#33231a] pt-4">
                                    <span className="text-[10px] uppercase tracking-[0.2em] text-[#9c7863]">Current user</span>
                                    <span className="font-mono text-[13px] font-bold tracking-wide">
                                        <span className="text-[#d6b7a0]">GUEST</span>{' '}
                                        <span className="text-[#f0a06f]">// 1,200 ELO</span>
                                    </span>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                </section>

                {/* ═══ INFO STRIP ═══ */}
                <section className="mt-12 grid grid-cols-1 divide-y divide-[#2f2017] border border-[#35251b] bg-[#1b120d]/88 sm:grid-cols-2 sm:divide-x sm:divide-y-0 xl:grid-cols-4">
                    {platformInfo.map((item, index) => (
                        <motion.div key={item.label} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.12 + index * 0.05, duration: 0.4 }} className="px-6 py-5">
                            <p className="text-[10px] uppercase tracking-[0.24em] text-[#9e7b66]">{item.label}</p>
                            <p className="mt-2 text-lg font-bold tracking-[-0.03em] text-[#f0a06f]">{item.value}</p>
                        </motion.div>
                    ))}
                </section>

                {/* ═══ FEATURES: FORGE YOUR REPUTATION ═══ */}
                <section className="mt-20">
                    <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45 }}>
                        <p className="text-[11px] uppercase tracking-[0.28em] text-[#a8846d]">Forge your reputation</p>
                        <h2 className="mt-4 text-4xl sm:text-5xl font-black tracking-[-0.05em] uppercase text-[#f6eadf]">
                            Everything you need to level up.
                        </h2>
                    </motion.div>

                    {/* Row 1: 1v1 Battles (visual) + ELO Rating */}
                    <div className="mt-10 grid gap-5 lg:grid-cols-[1.2fr_1fr]">
                        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.12, duration: 0.42 }} className="border border-[#3a281d] bg-[#1b120d]/90 p-6 sm:p-7">
                            <div className="flex items-center justify-between gap-4">
                                <p className="text-[10px] uppercase tracking-[0.24em] text-[#9e7b66]">1v1 matchmaking</p>
                                <Swords size={20} className="text-[#f0a06f]" />
                            </div>
                            <div className="mt-6 border border-[#3c2a1f] bg-[#140e0a] p-4 font-mono text-[11px] leading-7 text-[#9c7863]">
                                <div><span className="text-[#6c4d3b]">&gt;</span> queue.join(ranked=true)</div>
                                <div><span className="text-[#f0a06f]">&gt;</span> opponent found — match starting</div>
                                <div><span className="text-[#71945f]">&gt;</span> problem loaded — timer: 15:00</div>
                                <div><span className="text-[#f0a06f]">&gt;</span> both players coding live...</div>
                                <div className="mt-2"><span className="text-[#71945f]">&gt;</span> <span className="text-[#d6b7a0]">result: WIN +28 ELO</span></div>
                            </div>
                            <h3 className="mt-6 text-2xl sm:text-[1.8rem] leading-[1.06] font-black uppercase tracking-[-0.05em] text-[#f6eadf]">
                                Head-to-head battles in real time.
                            </h3>
                            <p className="mt-4 text-sm sm:text-base leading-relaxed text-[#d6b7a0]">
                                Queue up and get matched with a real opponent. Both of you solve the same problem under a shared timer. Your code runs against hidden tests — the faster and better solution wins.
                            </p>
                        </motion.div>

                        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.18, duration: 0.42 }} className="border border-[#3a281d] bg-[#1b120d]/90 p-6 sm:p-7 flex flex-col">
                            <div className="flex items-center justify-between gap-4">
                                <p className="text-[10px] uppercase tracking-[0.24em] text-[#9e7b66]">Rating system</p>
                                <BarChart3 size={20} className="text-[#f0a06f]" />
                            </div>
                            <h3 className="mt-6 text-2xl sm:text-[1.8rem] leading-[1.06] font-black uppercase tracking-[-0.05em] text-[#f6eadf]">
                                ELO that tracks your real skill.
                            </h3>
                            <p className="mt-4 text-sm sm:text-base leading-relaxed text-[#d6b7a0]">
                                Every match updates your ELO rating. Win and it goes up. Lose and it drops. No shortcuts — your rating shows how you actually perform against real opponents.
                            </p>
                            <div className="mt-auto pt-6 flex items-center justify-between border-t border-[#33231a]">
                                <span className="text-[10px] uppercase tracking-[0.2em] text-[#9c7863]">Current user</span>
                                <span className="font-mono text-[13px] font-bold tracking-wide">
                                    <span className="text-[#d6b7a0]">YOUR_NAME</span>{' '}
                                    <span className="text-[#f0a06f]">// 1,200 ELO</span>
                                </span>
                            </div>
                        </motion.div>
                    </div>

                    {/* Row 2: Company DSA — full width */}
                    <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.24, duration: 0.42 }} className="mt-5 border border-[#3a281d] bg-[#1b120d]/90 p-6 sm:p-7">
                        <div className="flex items-center justify-between gap-4">
                            <p className="text-[10px] uppercase tracking-[0.24em] text-[#9e7b66]">Company-wise DSA</p>
                            <Building2 size={20} className="text-[#f0a06f]" />
                        </div>
                        <h3 className="mt-6 text-2xl sm:text-[2rem] leading-[1.02] font-black uppercase tracking-[-0.05em] text-[#f6eadf]">
                            Practice problems asked by real companies.
                        </h3>
                        <p className="mt-5 max-w-3xl text-sm sm:text-base leading-relaxed text-[#d6b7a0]">
                            Pick a company — Google, Amazon, Microsoft, Meta, and more. Solve their most commonly asked interview problems with a proper code editor, hidden test cases, and AI feedback after every submission to help you understand what went right or wrong.
                        </p>
                    </motion.div>

                    {/* Row 3: CP + Secure Execution */}
                    <div className="mt-5 grid gap-5 md:grid-cols-2">
                        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.30, duration: 0.42 }} className="border border-[#3a281d] bg-[#1b120d]/90 p-6 sm:p-7">
                            <div className="flex items-center justify-between gap-4">
                                <p className="text-[10px] uppercase tracking-[0.24em] text-[#9e7b66]">Competitive programming</p>
                                <Code2 size={20} className="text-[#f0a06f]" />
                            </div>
                            <h3 className="mt-6 text-xl sm:text-2xl leading-[1.06] font-black uppercase tracking-[-0.05em] text-[#f6eadf]">
                                Codeforces-style practice with ratings.
                            </h3>
                            <p className="mt-4 text-sm leading-relaxed text-[#d6b7a0]">
                                Write full solutions with raw stdin and stdout. Problems are sorted by difficulty rating from 800 to 2000+, just like a competitive programming ladder.
                            </p>
                        </motion.div>

                        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.36, duration: 0.42 }} className="border border-[#3a281d] bg-[#1b120d]/90 p-6 sm:p-7">
                            <div className="flex items-center justify-between gap-4">
                                <p className="text-[10px] uppercase tracking-[0.24em] text-[#9e7b66]">Secure execution</p>
                                <Shield size={20} className="text-[#f0a06f]" />
                            </div>
                            <h3 className="mt-6 text-xl sm:text-2xl leading-[1.06] font-black uppercase tracking-[-0.05em] text-[#f6eadf]">
                                Every submission runs in isolation.
                            </h3>
                            <p className="mt-4 text-sm leading-relaxed text-[#d6b7a0]">
                                Your code runs inside Docker containers with hidden test cases. Both practice and battle submissions are judged by real execution — not mocked responses.
                            </p>
                        </motion.div>
                    </div>
                </section>

                {/* ═══ CTA ═══ */}
                <section className="mt-20 border border-[#3a281d] bg-[linear-gradient(180deg,rgba(33,22,16,0.98),rgba(24,16,12,0.98))] px-6 py-14 text-center sm:px-10">
                    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45 }}>
                        <h2 className="text-4xl sm:text-5xl font-black tracking-[-0.05em] uppercase text-[#f6eadf]">
                            Ready to enter the <span className="text-[#f0a06f]">arena</span>?
                        </h2>
                        <p className="mx-auto mt-5 max-w-2xl text-base sm:text-lg leading-relaxed text-[#d6b7a0]">
                            Battle other coders, practice interview problems, grind competitive programming, and track your progress with a real rating. No fluff. Just code and compete.
                        </p>
                        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                            <Link to={isAuthenticated ? '/problems' : '/register'} className="inline-flex items-center justify-center gap-3 bg-[#f0a06f] px-8 py-4 text-sm font-black uppercase tracking-[0.22em] text-[#1b120d] shadow-[0_14px_34px_rgba(240,160,111,0.14)] transition-transform hover:-translate-y-0.5">
                                {isAuthenticated ? 'Start practicing' : 'Join CodeArena'}
                                <ArrowRight size={18} />
                            </Link>
                            {!isAuthenticated && (
                                <Link to="/login" className="inline-flex items-center justify-center gap-3 border border-[#5d4435] bg-[#211610] px-8 py-4 text-sm font-bold uppercase tracking-[0.18em] text-[#f3e7da] transition-colors hover:border-[#8a6047] hover:bg-[#291b14]">
                                    Log in
                                </Link>
                            )}
                        </div>
                    </motion.div>
                </section>

                {/* ═══ FOOTER ═══ */}
                <footer className="mt-16 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-[#2f2017] pt-8 pb-4">
                    <span className="text-sm font-black uppercase tracking-[0.18em] text-[#f0a06f]">CodeArena</span>
                    <span className="text-[11px] text-[#7a6354] tracking-wide">
                        © {new Date().getFullYear()} CodeArena. All rights reserved.
                    </span>
                </footer>
            </div>
        </div>
    );
}
