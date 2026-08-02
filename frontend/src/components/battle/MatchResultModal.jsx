import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useBattleStore } from '../../stores/battleStore';
import { matchmakingApi, practiceApi } from '../../api/auth';
import { formatEloDelta } from '../../utils/formatters';
import { Trophy, Skull, Handshake, Clock, Share2, RotateCcw, Sparkles } from 'lucide-react';
import AIAnalysisPanel from '../ui/AIAnalysisPanel';

export default function MatchResultModal() {
    const matchResult = useBattleStore((s) => s.matchResult);
    const opponent = useBattleStore((s) => s.opponent);
    const reset = useBattleStore((s) => s.reset);
    const navigate = useNavigate();
    const navigatedRef = useRef(false);
    const pollIntervalRef = useRef(null);
    const [rematchLoading, setRematchLoading] = useState(false);
    const [aiLoading, setAiLoading] = useState(false);
    const [aiDebrief, setAiDebrief] = useState(null);
    const [showAi, setShowAi] = useState(false);
    const [rematchRoom, setRematchRoom] = useState(null);

    const aiBusy = aiLoading || showAi;
    const pauseAutoNav = aiBusy || !!rematchRoom;

    useEffect(() => {
        if (!matchResult || pauseAutoNav) return;
        navigatedRef.current = false;
        const timeout = setTimeout(() => {
            if (navigatedRef.current) return;
            navigatedRef.current = true;
            reset();
            navigate('/dashboard');
        }, 8000);
        return () => clearTimeout(timeout);
    }, [matchResult, pauseAutoNav, reset, navigate]);

    useEffect(() => () => {
        if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    }, []);

    if (!matchResult) return null;

    const { match_id, result, elo_change, winner_username, opponent_username, reason } = matchResult;
    const opponentName = opponent_username || opponent?.username || 'your opponent';

    const isWin = result === 'win';
    const isLoss = result === 'loss';
    const isTimeUp = result === 'time_up';
    const isDraw = result === 'draw' || isTimeUp;

    const Icon = isWin ? Trophy : isLoss ? Skull : isTimeUp ? Clock : Handshake;
    const title = isWin ? 'Victory' : isLoss ? 'Defeat' : isTimeUp ? "Time's Up!" : (reason === 'forfeit' ? 'Forfeit' : 'Draw');
    
    const colorClass = isWin ? 'text-win' : isLoss ? 'text-loss' : 'text-draw';
    const borderColorClass = isWin ? 'border-win' : isLoss ? 'border-loss' : 'border-draw';

    const goDashboard = () => {
        if (navigatedRef.current) return;
        navigatedRef.current = true;
        if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
        reset();
        navigate('/dashboard');
    };

    const handleShare = () => {
        if (!match_id) {
            toast.error('Recap not available yet');
            return;
        }
        const url = `${window.location.origin}/recap/${match_id}`;
        navigator.clipboard.writeText(url).then(
            () => toast.success('Recap link copied'),
            () => toast.error('Could not copy link'),
        );
    };

    const startRematchPoll = (code) => {
        if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = setInterval(async () => {
            try {
                const statusRes = await matchmakingApi.getPrivateRoomStatus(code);
                if (statusRes.status === 'matched' && statusRes.match_id) {
                    clearInterval(pollIntervalRef.current);
                    pollIntervalRef.current = null;
                    navigatedRef.current = true;
                    reset();
                    navigate(`/battle/${statusRes.match_id}`, { replace: true });
                }
            } catch (err) {
                console.error('Rematch poll error:', err);
            }
        }, 1000);
    };

    const handleRematch = async () => {
        setRematchLoading(true);
        try {
            const room = await matchmakingApi.createPrivateRoom();
            setRematchRoom(room);
            try {
                await navigator.clipboard.writeText(room.code);
                toast.success(`Room code ${room.code} copied — share with your opponent`);
            } catch {
                toast.success(`Room code ${room.code} — share with your opponent`);
            }
            startRematchPoll(room.code);
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to create rematch room');
        } finally {
            setRematchLoading(false);
        }
    };

    const handleCancelRematch = () => {
        if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
        }
        setRematchRoom(null);
        navigatedRef.current = false;
        goDashboard();
    };

    const handleReviewAI = async () => {
        if (!match_id) return;
        setAiLoading(true);
        try {
            const res = await practiceApi.analyzeMatch(match_id);
            setAiDebrief({
                analysis: res.analysis,
                verdict: res.verdict || (result === 'win' ? 'accepted' : 'wrong_answer'),
            });
            setShowAi(true);
        } catch (err) {
            toast.error(err.response?.data?.detail || 'No submission to analyze');
        } finally {
            setAiLoading(false);
        }
    };

    const handleCloseAi = () => {
        setShowAi(false);
        // Stay on result modal; auto-nav resumes when AI closed
    };

    if (showAi && aiDebrief) {
        return (
            <AIAnalysisPanel
                analysis={aiDebrief.analysis}
                verdict={{ status: aiDebrief.verdict }}
                onClose={handleCloseAi}
            />
        );
    }

    if (rematchRoom) {
        return (
            <div className="fixed inset-0 z-[400] flex items-end sm:items-center justify-center bg-bg-root/90 backdrop-blur-sm p-0 sm:p-4">
                <div className="bg-bg-primary border border-border border-t-4 border-t-accent p-6 sm:p-8 w-full sm:w-auto sm:min-w-[360px] max-w-lg rounded-t-2xl sm:rounded-none shadow-2xl">
                    <div className="flex flex-col items-center text-center gap-4">
                        <h2 className="text-xl font-bold text-text-primary">Waiting for Opponent</h2>
                        <p className="text-sm text-text-secondary">
                            Share this code with your opponent to rematch:
                        </p>
                        <div className="w-full py-4 px-6 bg-bg-surface border border-border rounded-sm">
                            <p className="text-3xl font-mono font-bold tracking-[0.2em] text-accent">
                                {rematchRoom.code}
                            </p>
                        </div>
                        <p className="text-xs text-text-muted flex items-center gap-2">
                            <span className="w-3.5 h-3.5 border-2 border-accent/30 border-t-accent rounded-full animate-spin" />
                            Waiting for them to join...
                        </p>
                        <button
                            type="button"
                            onClick={handleCancelRematch}
                            className="w-full px-4 py-2 bg-bg-surface border border-border text-sm font-semibold text-text-primary hover:bg-bg-hover transition-colors rounded-sm"
                        >
                            Cancel &amp; Return to Dashboard
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 z-[400] flex items-end sm:items-center justify-center bg-bg-root/90 backdrop-blur-sm animate-in fade-in duration-200 p-0 sm:p-4">
            <div className={`bg-bg-primary border ${borderColorClass} border-t-4 p-6 sm:p-8 w-full sm:w-auto sm:min-w-[360px] max-w-lg max-h-[90dvh] overflow-y-auto shadow-2xl relative rounded-t-2xl sm:rounded-none`}>
                <div className="flex flex-col items-center text-center">
                    <Icon className={`w-12 h-12 mb-4 ${colorClass}`} />
                    <h2 className={`text-2xl font-bold tracking-tight mb-2 ${colorClass}`}>
                        {title}
                    </h2>
                    <p className="text-sm text-text-secondary mb-6 sm:mb-8 px-1">
                        {isWin && (reason === 'forfeit'
                            ? `${opponentName} forfeited.`
                            : `You solved all problems before ${opponentName}.`)}
                        {isLoss && (reason === 'forfeit'
                            ? 'You forfeited the match.'
                            : `${winner_username && winner_username !== 'You' ? winner_username : opponentName} solved all problems first.`)}
                        {isTimeUp && 'Neither player solved all problems in time. No rating change.'}
                        {isDraw && !isTimeUp && reason !== 'forfeit' && 'The match ended in a draw.'}
                    </p>

                    {elo_change != null && (
                        <div className="flex flex-col items-center justify-center mb-6 px-8 py-4 bg-bg-surface border border-border rounded-sm w-full">
                            <div className={`font-mono text-2xl font-bold ${isTimeUp ? 'text-text-muted' : elo_change >= 0 ? 'text-win' : 'text-loss'}`}>
                                {formatEloDelta(elo_change)}
                            </div>
                            <div className="text-[10px] uppercase font-bold tracking-wider text-text-muted mt-1">
                                {isTimeUp ? 'No Rating Change' : 'Rating Change'}
                            </div>
                        </div>
                    )}

                    <div className="flex flex-col gap-2 w-full mb-3">
                        {match_id && (
                            <button
                                type="button"
                                disabled={aiLoading}
                                onClick={handleReviewAI}
                                className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-accent/10 border border-accent/30 text-sm font-medium text-accent hover:bg-accent/20 disabled:opacity-50"
                            >
                                <Sparkles size={14} />
                                {aiLoading ? 'Analyzing...' : 'Review with AI'}
                            </button>
                        )}
                        <div className="flex gap-2 w-full">
                        {match_id && (
                            <button
                                type="button"
                                onClick={handleShare}
                                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-bg-surface border border-border text-sm font-medium hover:bg-bg-hover"
                            >
                                <Share2 size={14} />
                                Share
                            </button>
                        )}
                        <button
                            type="button"
                            disabled={rematchLoading}
                            onClick={handleRematch}
                            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-bg-surface border border-border text-sm font-medium hover:bg-bg-hover disabled:opacity-50"
                        >
                            <RotateCcw size={14} />
                            {rematchLoading ? '...' : 'Rematch'}
                        </button>
                        </div>
                    </div>

                    <button 
                        type="button"
                        className="w-full px-4 py-2 bg-bg-surface border border-border text-sm font-semibold text-text-primary hover:bg-bg-hover hover:border-text-muted transition-colors rounded-sm"
                        onClick={goDashboard}
                    >
                        Return to Dashboard
                    </button>
                </div>
                
                {!pauseAutoNav && (
                    <div className="absolute bottom-0 left-0 h-0.5 bg-bg-surface w-full">
                        <div className="h-full bg-text-muted animate-[shrink_8s_linear_forwards]" style={{ transformOrigin: 'left' }} />
                    </div>
                )}
            </div>
            
            <style>{`
                @keyframes shrink {
                    from { transform: scaleX(1); }
                    to { transform: scaleX(0); }
                }
            `}</style>
        </div>
    );
}
