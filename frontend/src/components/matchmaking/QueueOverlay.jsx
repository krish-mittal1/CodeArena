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
                    className="relative w-full max-w-md mx-4 bg-bg-elevated border border-border rounded-2xl p-8 text-center shadow-2xl"
                >
                    {status === 'searching' && (
                        <>
                            {/* Animated Swords */}
                            <motion.div
                                animate={{ scale: [1, 1.1, 1], rotate: [0, 5, -5, 0] }}
                                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                                className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-accent to-accent-secondary flex items-center justify-center shadow-xl mb-6"
                                style={{ boxShadow: '0 0 40px rgba(124, 92, 252, 0.3)' }}
                            >
                                <Swords size={36} className="text-white" />
                            </motion.div>

                            <h2 className="text-2xl font-bold text-text-primary mb-2">Finding Opponent</h2>
                            <p className="text-sm text-text-secondary mb-6">
                                Matching you with a player near your skill level
                            </p>

                            {/* Timer */}
                            <div className="bg-bg-surface rounded-xl px-6 py-4 mb-6 inline-block">
                                <p className="text-3xl font-mono font-bold text-accent">{formatTime(waitSeconds)}</p>
                                <p className="text-xs text-text-muted mt-1">Time in Queue</p>
                            </div>

                            {/* Estimated Wait */}
                            <p className="text-xs text-text-muted mb-6">
                                Estimated wait: ~{Math.max(10, 30 - waitSeconds)}s
                            </p>

                            {/* Loading Dots */}
                            <div className="flex justify-center gap-2 mb-6">
                                {[0, 1, 2].map((i) => (
                                    <motion.div
                                        key={i}
                                        animate={{ scale: [1, 1.4, 1], opacity: [0.3, 1, 0.3] }}
                                        transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
                                        className="w-2.5 h-2.5 rounded-full bg-accent"
                                    />
                                ))}
                            </div>

                            {error && (
                                <div className="bg-loss/10 border border-loss/20 text-loss text-sm rounded-xl px-4 py-2 mb-4">
                                    {error}
                                </div>
                            )}

                            <Button variant="danger" size="md" onClick={leaveQueue} className="w-full">
                                <X size={16} />
                                Cancel Search
                            </Button>
                        </>
                    )}

                    {status === 'found' && (
                        <>
                            <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ type: 'spring', damping: 10, stiffness: 200 }}
                                className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-win/80 to-accent-secondary flex items-center justify-center shadow-xl mb-6"
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
