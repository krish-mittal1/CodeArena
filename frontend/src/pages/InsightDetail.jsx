import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Share2, ArrowLeft } from 'lucide-react';
import { insightsApi } from '../api/auth';
import AIAnalysisPanel from '../components/ui/AIAnalysisPanel';

export default function InsightDetail() {
    const { insightId } = useParams();
    const navigate = useNavigate();
    const { data, isLoading } = useQuery({
        queryKey: ['insight', insightId],
        queryFn: () => insightsApi.get(insightId),
        enabled: !!insightId,
    });

    const handleShare = () => {
        if (!data?.share_slug) return;
        const url = `${window.location.origin}/insight/${data.share_slug}`;
        navigator.clipboard.writeText(url).then(
            () => toast.success('Insight link copied'),
            () => toast.error('Could not copy'),
        );
    };

    if (isLoading || !data) {
        return <div className="min-h-screen bg-bg-root flex items-center justify-center text-text-secondary text-sm">Loading...</div>;
    }

    return (
        <div className="min-h-screen bg-bg-root">
            <div className="max-w-3xl mx-auto px-6 py-8">
                <button type="button" onClick={() => navigate('/insights')} className="flex items-center gap-2 text-sm text-text-secondary mb-6 hover:text-text-primary">
                    <ArrowLeft size={16} /> Back to library
                </button>
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h1 className="text-xl font-bold text-text-primary">{data.problem_title}</h1>
                        <p className="text-sm text-text-muted">{data.topic} · {data.verdict}</p>
                    </div>
                    {data.share_slug && (
                        <button type="button" onClick={handleShare} className="flex items-center gap-2 px-3 py-2 border border-border text-sm hover:bg-bg-hover">
                            <Share2 size={14} /> Share
                        </button>
                    )}
                </div>
                <AIAnalysisPanel analysis={data.analysis} verdict={data.verdict} failedTestCase={data.analysis?.failed_test_explanation ? null : null} />
            </div>
        </div>
    );
}
