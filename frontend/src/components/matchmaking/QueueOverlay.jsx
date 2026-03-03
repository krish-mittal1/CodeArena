import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Swords, X, Loader2 } from 'lucide-react';
import { useMatchmakingStore } from '../../stores/matchmakingStore';
import { formatTime } from '../../utils/formatters';
import Button from '../ui/Button';

export default function QueueOverlay() {
    const status = useMatchmakingStore((s) => s.status);
    const waitSeconds = useMatchmakingStore((s) => s.waitSeconds);
    const matchData = useMatchmakingStore((s) => s.matchData);
    const error = useMatchmakingStore((s) => s.error);
    const leaveQueue = useMatchmakingStore((s) => s.leaveQueue);
    const tickWait = useMatchmakingStore((s) => s.tickWait);
    const reset = useMatchmakingStore((s) => s.reset);

    const navigate = useNavigate();
    const tickRef = useRef(null);
    const hasNavigatedRef = useRef(false);

    useEffect(() => {
        if (status === 'searching') {
            tickRef.current = setInterval(() => tickWait(), 1000);
        }
        return () => {
            if (tickRef.current) clearInterval(tickRef.current);
        };
    }, [status, tickWait]);

    useEffect(() => {
        if (status === 'found' && matchData?.match_id && !hasNavigatedRef.current) {
            hasNavigatedRef.current = true;
            const matchId = matchData.match_id;
            navigate(`/battle/${matchId}`, { replace: true });
            setTimeout(() => {
                reset();
                hasNavigatedRef.current = false;
            }, 100);
        }
    }, [status, matchData, navigate, reset]);

    if (status === 'idle') return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-[700] flex items-center justify-center bg-black/80 backdrop-blur-md"
            >
                <motion.div
                    initial={{ opacity: 0, scale: 0.9, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9, y: 20 }}
                    transition={{ type: 'spring', duration: 0.5 }}
                    className="relative w-full max-w-md mx-4 bg-bg-elevated border border-border rounded-xl p-8 sm:p-10 shadow-xl overflow-hidden"
                >
                    {/* Top Accent Line */}
                    <div className="absolute top-0 left-0 w-full h-1 bg-accent" />

                    {status === 'searching' && (
                        <div className="flex flex-col items-center justify-between w-full min-h-[420px] gap-8 mt-2">
                            {/* Top Section: Icon & Text */}
                            <div className="flex flex-col items-center gap-5 w-full">
                                {/* Animated Swords Badge */}
                                <motion.div
                                    animate={{ scale: [1, 1.05, 1], rotate: [0, 5, -5, 0] }}
                                    transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                                    className="w-14 h-14 rounded-xl bg-accent flex items-center justify-center"
                                >
                                    <Swords size={32} className="text-white drop-shadow-md" />
                                </motion.div>

                                {/* Typography */}
                                <div>
                                    <h2 className="text-2xl font-bold text-white mb-2 text-center tracking-wide">
                                        Finding Opponent
                                    </h2>
                                    <p className="text-sm text-gray-400 text-center max-w-[280px] mx-auto leading-relaxed">
                                        Matching you with a player near your skill level...
                                    </p>
                                </div>
                            </div>

                            {/* Middle Section: Timer & Loader */}
                            <div className="flex flex-col items-center gap-6 w-full mt-2">
                                {/* Timer Badge */}
                                <div className="flex flex-col items-center">
                                    <p className="text-xs font-bold tracking-widest text-gray-400 uppercase mb-3 drop-shadow-sm">
                                        Time in Queue
                                    </p>
                                    <div className="bg-accent/10 border border-accent/20 rounded-full px-8 py-3 inline-block">
                                        <p className="text-3xl font-mono text-accent font-bold tracking-wider relative bottom-[1px]">
                                            {formatTime(waitSeconds)}
                                        </p>
                                    </div>
                                    <p className="text-xs text-text-muted mt-4 font-medium tracking-wide">
                                        Estimated wait: ~{Math.max(10, 30 - waitSeconds)}s
                                    </p>
                                </div>

                                {/* Center Aligned Loading Dots */}
                                <div className="flex items-center justify-center gap-2 h-4 my-2">
                                    {[0, 1, 2].map((i) => (
                                        <motion.div
                                            key={i}
                                            animate={{ opacity: [0.2, 1, 0.2], scale: [0.8, 1.2, 0.8] }}
                                            transition={{ duration: 1.4, repeat: Infinity, delay: i * 0.2, ease: "easeInOut" }}
                                            className="w-2.5 h-2.5 rounded-full bg-accent"
                                        />
                                    ))}
                                </div>
                            </div>

                            {/* Bottom Section: Error & Cancel */}
                            <div className="w-full flex flex-col gap-4 mt-2">
                                {/* Error Message */}
                                {error && (
                                    <div className="bg-red-500/10 border border-red-500/20 text-red-500 text-sm rounded-xl px-4 py-3 w-full text-center">
                                        {error}
                                    </div>
                                )}

                                {/* Cancel Button */}
                                <button
                                    onClick={leaveQueue}
                                    className="w-full flex items-center justify-center gap-2 py-4 bg-loss/10 text-loss hover:bg-loss/20 border border-loss/20 transition-colors rounded-lg font-semibold text-base"
                                >
                                    <X size={20} />
                                    Cancel Search
                                </button>
                            </div>
                        </div>
                    )}

                    {status === 'found' && (
                        <>
                            <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ type: 'spring', damping: 10, stiffness: 200 }}
                                className="w-20 h-20 mx-auto rounded-xl bg-win flex items-center justify-center mb-6"
                            >
                                <span className="text-3xl">🎯</span>
                            </motion.div>
                            <h2 className="text-2xl font-bold text-win mb-2">Match Found!</h2>
                            <p className="text-sm text-text-secondary">
                                Opponent: <strong className="text-text-primary">{matchData?.opponent?.username ?? 'Unknown'}</strong>
                                {matchData?.opponent?.elo && (
                                    <span className="text-accent ml-2">· {matchData.opponent.elo} ELO</span>
                                )}
                            </p>
                        </>
                    )}
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}
