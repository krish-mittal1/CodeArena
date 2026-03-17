import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useBattleStore } from '../../stores/battleStore';
import { formatEloDelta } from '../../utils/formatters';
import { Trophy, Skull, Handshake } from 'lucide-react';

export default function MatchResultModal() {
    const matchResult = useBattleStore((s) => s.matchResult);
    const reset = useBattleStore((s) => s.reset);
    const navigate = useNavigate();

    useEffect(() => {
        if (!matchResult) return;
        const timeout = setTimeout(() => {
            reset();
            navigate('/dashboard');
        }, 5000);
        return () => clearTimeout(timeout);
    }, [matchResult, reset, navigate]);

    if (!matchResult) return null;

    const { result, elo_change, winner_username, reason } = matchResult;

    const isWin = result === 'win';
    const isLoss = result === 'loss';
    const isDraw = result === 'draw' || result === 'time_up';

    const Icon = isWin ? Trophy : isLoss ? Skull : Handshake;
    const title = isWin ? 'Victory' : isLoss ? 'Defeat' : (reason === 'forfeit' ? 'Forfeit' : 'Draw');
    
    const colorClass = isWin ? 'text-win' : isLoss ? 'text-loss' : 'text-draw';
    const borderColorClass = isWin ? 'border-win' : isLoss ? 'border-loss' : 'border-draw';

    const handleDashboard = () => {
        reset();
        navigate('/dashboard');
    };

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
                        {isDraw && reason !== 'forfeit' && 'Neither player solved the problem in time.'}
                    </p>

                    {elo_change != null && (
                        <div className="flex flex-col items-center justify-center mb-8 px-8 py-4 bg-bg-surface border border-border rounded-sm w-full">
                            <div className={`font-mono text-2xl font-bold ${elo_change >= 0 ? 'text-win' : 'text-loss'}`}>
                                {formatEloDelta(elo_change)}
                            </div>
                            <div className="text-[10px] uppercase font-bold tracking-wider text-text-muted mt-1">
                                Rating Change
                            </div>
                        </div>
                    )}

                    <button 
                        className="w-full px-4 py-2 bg-bg-surface border border-border text-sm font-semibold text-text-primary hover:bg-bg-hover hover:border-text-muted transition-colors rounded-sm"
                        onClick={handleDashboard}
                    >
                        Return to Dashboard
                    </button>
                </div>
                
                {/* Auto close progress indicator */}
                <div className="absolute bottom-0 left-0 h-0.5 bg-bg-surface w-full">
                    <div className="h-full bg-text-muted animate-[shrink_5s_linear_forwards]" style={{ transformOrigin: 'left' }} />
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
