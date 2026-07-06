import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Share2, Swords } from 'lucide-react';
import dayjs from 'dayjs';
import toast from 'react-hot-toast';
import { matchApi } from '../api/auth';
import { formatEloDelta } from '../utils/formatters';

export default function MatchRecap() {
    const { matchId } = useParams();

    const { data: recap, isLoading, isError } = useQuery({
        queryKey: ['matchRecap', matchId],
        queryFn: () => matchApi.getRecap(matchId),
        enabled: !!matchId,
    });

    const handleShare = () => {
        const url = window.location.href;
        navigator.clipboard.writeText(url).then(
            () => toast.success('Recap link copied'),
            () => toast.error('Could not copy link'),
        );
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-bg-root flex items-center justify-center">
                <p className="text-text-secondary text-sm">Loading recap...</p>
            </div>
        );
    }

    if (isError || !recap) {
        return (
            <div className="min-h-screen bg-bg-root flex flex-col items-center justify-center gap-4">
                <p className="text-loss text-sm">Recap not found</p>
                <Link to="/" className="text-accent text-sm hover:underline">Back home</Link>
            </div>
        );
    }

    const winner = recap.winner_username;

    return (
        <div className="min-h-screen bg-bg-root flex items-center justify-center p-6">
            <div className="bg-bg-primary border border-border max-w-md w-full p-8 shadow-xl">
                <div className="flex items-center gap-3 mb-6">
                    <Swords size={22} className="text-accent" />
                    <div>
                        <p className="editorial-kicker">Match recap</p>
                        <h1 className="text-lg font-bold text-text-primary">{recap.problem_title}</h1>
                    </div>
                </div>

                <div className="space-y-4 mb-6 text-sm">
                    <div className="flex justify-between border-b border-border/50 pb-2">
                        <span className="text-text-secondary">{recap.player1_username}</span>
                        <span className={`font-mono ${recap.player1_elo_delta >= 0 ? 'text-win' : 'text-loss'}`}>
                            {formatEloDelta(recap.player1_elo_delta)}
                        </span>
                    </div>
                    <div className="flex justify-between border-b border-border/50 pb-2">
                        <span className="text-text-secondary">{recap.player2_username}</span>
                        <span className={`font-mono ${recap.player2_elo_delta >= 0 ? 'text-win' : 'text-loss'}`}>
                            {formatEloDelta(recap.player2_elo_delta)}
                        </span>
                    </div>
                </div>

                <p className="text-center text-text-primary font-semibold mb-1">
                    {winner ? `${winner} wins` : 'Draw'}
                </p>
                {recap.ended_at && (
                    <p className="text-center text-xs text-text-muted mb-6">
                        {dayjs(recap.ended_at).format('MMM D, YYYY h:mm A')}
                    </p>
                )}

                <button
                    type="button"
                    onClick={handleShare}
                    className="w-full flex items-center justify-center gap-2 py-2.5 border border-border text-sm font-medium hover:bg-bg-hover"
                >
                    <Share2 size={16} />
                    Copy share link
                </button>

                <Link
                    to="/dashboard"
                    className="block text-center text-accent text-sm mt-4 hover:underline"
                >
                    Play on CodeArena
                </Link>
            </div>
        </div>
    );
}
