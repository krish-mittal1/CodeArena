import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Sparkles } from 'lucide-react';
import { insightsApi } from '../api/auth';

export default function InsightShare() {
    const { shareSlug } = useParams();
    const { data, isLoading, isError } = useQuery({
        queryKey: ['insightShare', shareSlug],
        queryFn: () => insightsApi.getShared(shareSlug),
        enabled: !!shareSlug,
    });

    if (isLoading) return <div className="min-h-screen bg-bg-root flex items-center justify-center text-sm text-text-secondary">Loading...</div>;
    if (isError || !data) return <div className="min-h-screen bg-bg-root flex items-center justify-center text-sm text-loss">Insight not found</div>;

    const tips = data.analysis?.tips || [];

    return (
        <div className="min-h-screen bg-bg-root flex items-center justify-center p-6">
            <div className="bg-bg-primary border border-border max-w-md w-full p-8 shadow-xl">
                <div className="flex items-center gap-2 mb-4">
                    <Sparkles className="text-accent" size={20} />
                    <span className="text-xs uppercase tracking-wider text-text-muted">CodeArena insight</span>
                </div>
                <h1 className="text-lg font-bold text-text-primary">{data.problem_title}</h1>
                <p className="text-sm text-text-muted mb-4">{data.topic} · {data.verdict}</p>
                <p className="text-sm text-text-secondary whitespace-pre-wrap mb-4">{data.analysis?.optimized_approach?.slice(0, 400)}...</p>
                {tips[0] && (
                    <p className="text-sm border-l-2 border-accent pl-3 text-text-primary">
                        Tip: {tips[0]}
                    </p>
                )}
                <a href="/" className="block text-center text-accent text-sm mt-6 hover:underline">Practice on CodeArena</a>
            </div>
        </div>
    );
}
