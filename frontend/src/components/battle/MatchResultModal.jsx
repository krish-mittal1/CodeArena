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
    const reset = useBattleStore((s) => s.reset);
    const navigate = useNavigate();
    const navigatedRef = useRef(false);
    const [rematchLoading, setRematchLoading] = useState(false);
    const [aiLoading, setAiLoading] = useState(false);
    const [aiDebrief, setAiDebrief] = useState(null);
    const [showAi, setShowAi] = useState(false);

    useEffect(() => {
        if (!matchResult) return;
        navigatedRef.current = false;
        const timeout = setTimeout(() => {
            if (navigatedRef.current) return;
            navigatedRef.current = true;
            reset();
            navigate('/dashboard');
        }, 8000);
        return () => clearTimeout(timeout);
    }, [matchResult, reset, navigate]);

    if (!matchResult) return null;

    const { match_id, result, elo_change, winner_username, reason } = matchResult;

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

    const handleRematch = async () => {
        setRematchLoading(true);
        try {
            const room = await matchmakingApi.createPrivateRoom();
            navigatedRef.current = true;
            reset();
            await navigator.clipboard.writeText(room.code);
            toast.success(`Room code ${room.code} copied — share with your opponent`);
            navigate('/dashboard');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Failed to create rematch room');
        } finally {
            setRematchLoading(false);
        }
    };

    const handleReviewAI = async () => {
        if (!match_id) return;
        setAiLoading(true);
        try {
            const res = await practiceApi.analyzeMatch(match_id);
            setAiDebrief(res.analysis);
            setShowAi(true);
        } catch (err) {
            toast.error(err.response?.data?.detail || 'No submission to analyze');
        } finally {
            setAiLoading(false);
        }
    };

    if (showAi && aiDebrief) {
        return (
            <AIAnalysisPanel
                analysis={aiDebrief}
                verdict={{ status: result === 'win' ? 'accepted' : 'wrong_answer' }}
                onClose={() => { setShowAi(false); goDashboard(); }}
            />
        );
    }

    return (
        <div className="fixed inset-0 z-[400] flex items-center justify-center bg-bg-root/90 backdrop-blur-sm animate-in fade-in duration-200">
            <div className={`bg-bg-primary border ${borderColorClass} border-t-4 p-8 min-w-[380px] max-w-lg shadow-2xl relative`}>
                <div className="flex flex-col items-center text-center">
                    <Icon className={`w-12 h-12 mb-4 ${colorClass}`} />
                    <h2 className={`text-2xl font-bold tracking-tight mb-2 ${colorClass}`}>
                        {title}
                    </h2>
                    <p className="text-sm text-text-secondary mb-8">
                        {isWin && (reason === 'forfeit'
                            ? `${winner_username || 'Your opponent'} forfeited.`
                            : `You solved it before ${winner_username || 'your opponent'}.`)}
                        {isLoss && (reason === 'forfeit'
                            ? 'You forfeited the match.'
                            : `${winner_username || 'Your opponent'} solved it first.`)}
                        {isTimeUp && 'Neither player solved the problem in time. No rating change.'}
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
                
                <div className="absolute bottom-0 left-0 h-0.5 bg-bg-surface w-full">
                    <div className="h-full bg-text-muted animate-[shrink_8s_linear_forwards]" style={{ transformOrigin: 'left' }} />
                </div>
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
