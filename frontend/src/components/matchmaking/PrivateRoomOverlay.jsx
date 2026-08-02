import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Users, UserPlus, X, Loader2, Copy, CheckCircle2 } from 'lucide-react';
import { matchmakingApi } from '../../api/auth';
import { useBattleStore } from '../../stores/battleStore';

export default function PrivateRoomOverlay({ isOpen, onClose }) {
    const navigate = useNavigate();
    const battleMatchId = useBattleStore((s) => s.matchId);
    
    // 'select' | 'create' | 'join'
    const [view, setView] = useState('select');
    
    // Create state
    const [roomCode, setRoomCode] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [copied, setCopied] = useState(false);
    const pollIntervalRef = useRef(null);
    const waitingRef = useRef(false);

    // Join state
    const [joinInput, setJoinInput] = useState('');
    const [isJoining, setIsJoining] = useState(false);
    const [joinError, setJoinError] = useState('');

    const clearPoll = () => {
        if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
        }
    };

    const handleCancel = () => {
        waitingRef.current = false;
        clearPoll();
        onClose();
    };

    useEffect(() => {
        if (!isOpen) {
            // Keep poll alive while waiting for opponent — only tear down on cancel
            // or when battle has loaded (handled below / unmount).
            if (!waitingRef.current) {
                setView('select');
                setRoomCode('');
                setJoinInput('');
                setJoinError('');
                setIsCreating(false);
                setIsJoining(false);
                clearPoll();
            }
        }
    }, [isOpen]);

    // When WS/battle store gets a match while we're waiting, navigate and stop poll
    useEffect(() => {
        if (!waitingRef.current || !battleMatchId) return;
        clearPoll();
        waitingRef.current = false;
        navigate(`/battle/${battleMatchId}`, { replace: true });
        onClose();
    }, [battleMatchId, navigate, onClose]);

    // Cleanup interval on unmount
    useEffect(() => {
        return () => {
            clearPoll();
        };
    }, []);

    // ── Generate Create Room Shortcode ──
    const handleCreateRoom = async () => {
        setView('create');
        setIsCreating(true);
        try {
            const res = await matchmakingApi.createPrivateRoom();
            setRoomCode(res.code);
            waitingRef.current = true;
            
            // Poll until battle loaded or user cancels
            pollIntervalRef.current = setInterval(async () => {
                try {
                    const statusRes = await matchmakingApi.getPrivateRoomStatus(res.code);
                    if (statusRes.status === 'matched' && statusRes.match_id) {
                        clearPoll();
                        waitingRef.current = false;
                        navigate(`/battle/${statusRes.match_id}`, { replace: true });
                        onClose();
                    }
                } catch (err) {
                    console.error("Polling error:", err);
                }
            }, 1000);
            
        } catch (err) {
            console.error("Failed to create room:", err);
            waitingRef.current = false;
            toast.error(err.response?.data?.detail || err.response?.data?.error || 'Failed to create room');
            setView('select');
        } finally {
            setIsCreating(false);
        }
    };

    // ── Join Existing Room ──
    const handleJoinRoom = async (e) => {
        e.preventDefault();
        const code = joinInput.trim().toUpperCase();
        if (code.length !== 6) {
            setJoinError("Room code must be 6 characters");
            return;
        }

        setIsJoining(true);
        setJoinError('');

        try {
            const res = await matchmakingApi.joinPrivateRoom(code);
            if (res.status === 'matched') {
                waitingRef.current = false;
                clearPoll();
                navigate(`/battle/${res.match_id}`, { replace: true });
                onClose();
            }
        } catch (err) {
            setJoinError(err.response?.data?.error || err.response?.data?.detail || "Failed to join room");
        } finally {
            setIsJoining(false);
        }
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(roomCode);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-[700] flex items-end sm:items-center justify-center bg-black/78 backdrop-blur-sm p-0 sm:p-4"
            >
                <div className="absolute inset-0 cursor-pointer" onClick={handleCancel} />
                <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: 10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: 10 }}
                    transition={{ type: 'spring', duration: 0.5 }}
                    className="relative w-full sm:max-w-sm sm:mx-0 mx-0 paper-card grain-panel p-5 sm:p-8 overflow-y-auto max-h-[min(92dvh,640px)] rounded-t-2xl sm:rounded-[inherit]"
                >
                    <button 
                        onClick={handleCancel}
                        className="absolute top-4 right-4 text-text-muted hover:text-text-primary transition-colors rounded-[12px_9px_11px_8px] p-1 hover:bg-bg-hover"
                    >
                        <X size={20} />
                    </button>

                    {view === 'select' && (
                        <div className="flex flex-col items-center gap-6 mt-2">
                            <div className="w-12 h-12 rounded-[16px_12px_14px_10px] bg-accent/10 flex items-center justify-center mb-2 shadow-[2px_2px_0_rgba(0,0,0,0.14)]">
                                <Users size={28} className="text-accent" />
                            </div>
                            <div className="text-center">
                                <p className="editorial-kicker mb-2">Private match</p>
                                <h2 className="text-2xl font-bold text-text-primary mb-2 tracking-[-0.04em]">Play with Friend</h2>
                                <p className="text-sm text-text-secondary">Create a private match or join an existing one using a room code.</p>
                            </div>

                            <div className="w-full flex flex-col gap-3 mt-4">
                                <button
                                    onClick={handleCreateRoom}
                                    className="w-full py-4 px-4 bg-accent hover:bg-accent-hover text-white rounded-[18px_14px_16px_12px] font-bold transition-colors flex items-center justify-center gap-2 border border-[#e29a6c] shadow-[4px_4px_0_rgba(0,0,0,0.18)]"
                                >
                                    <Users size={18} />
                                    Create Room
                                </button>
                                <button
                                    onClick={() => setView('join')}
                                    className="w-full py-4 px-4 bg-bg-surface hover:bg-bg-hover text-text-primary border border-border rounded-[18px_14px_16px_12px] font-semibold transition-colors flex items-center justify-center gap-2 shadow-[3px_3px_0_rgba(0,0,0,0.12)]"
                                >
                                    <UserPlus size={18} />
                                    Join Room
                                </button>
                            </div>
                        </div>
                    )}

                    {view === 'create' && (
                        <div className="flex flex-col items-center gap-6 mt-2">
                            <h2 className="text-2xl font-bold text-text-primary mb-2 tracking-[-0.04em]">Waiting for Friend</h2>
                            
                            {isCreating ? (
                                <div className="py-8 flex flex-col items-center justify-center gap-4">
                                    <Loader2 size={32} className="text-accent animate-spin" />
                                    <p className="text-sm text-text-secondary">Generating room code...</p>
                                </div>
                            ) : (
                                <div className="w-full flex flex-col items-center gap-6">
                                    <p className="text-sm text-text-secondary text-center">
                                        Share this code with your friend to connect instantly:
                                    </p>
                                    
                                    <div className="human-input p-6 w-full relative group">
                                        <p className="text-4xl font-mono text-center font-bold tracking-[0.2em] text-accent">
                                            {roomCode}
                                        </p>
                                        <button 
                                            onClick={copyToClipboard}
                                            className="absolute top-2 right-2 p-2 rounded-[12px_9px_11px_8px] bg-bg-surface hover:bg-bg-hover text-text-muted hover:text-white transition-colors"
                                            title="Copy Code"
                                        >
                                            {copied ? <CheckCircle2 size={16} className="text-win" /> : <Copy size={16} />}
                                        </button>
                                    </div>
                                    
                                    <div className="flex items-center gap-2 text-sm text-text-muted mt-2">
                                        <Loader2 size={16} className="animate-spin text-accent" />
                                        Waiting for them to join...
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {view === 'join' && (
                        <div className="flex flex-col items-center gap-6 mt-2">
                            <h2 className="text-2xl font-bold text-text-primary mb-2 tracking-[-0.04em]">Join Room</h2>
                            <p className="text-sm text-text-secondary text-center mb-2">
                                Enter the 6-character room code from your friend.
                            </p>

                            <form onSubmit={handleJoinRoom} className="w-full flex flex-col gap-4">
                                <input
                                    type="text"
                                    value={joinInput}
                                    onChange={(e) => setJoinInput(e.target.value.toUpperCase())}
                                    placeholder="e.g. A1B2C3"
                                    maxLength={6}
                                    className="w-full human-input text-center text-3xl font-mono font-bold py-4 outline-none transition-colors tracking-[0.2em] uppercase placeholder:text-text-muted/30"
                                    autoFocus
                                />
                                {joinError && (
                                    <p className="text-xs text-loss text-center font-medium bg-loss/10 py-2 rounded-[12px_9px_11px_8px] border border-loss/20">
                                        {joinError}
                                    </p>
                                )}
                                
                                <button
                                    type="submit"
                                    disabled={isJoining || joinInput.length !== 6}
                                    className="w-full py-4 bg-accent hover:bg-accent-hover text-white rounded-[18px_14px_16px_12px] font-bold transition-colors border border-[#e29a6c] shadow-[4px_4px_0_rgba(0,0,0,0.18)] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-4"
                                >
                                    {isJoining ? (
                                        <><Loader2 size={18} className="animate-spin" /> Joining...</>
                                    ) : (
                                        'Join Match'
                                    )}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setView('select')}
                                    className="text-sm text-text-muted hover:text-white transition-colors mt-2"
                                >
                                    Back
                                </button>
                            </form>
                        </div>
                    )}

                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}
