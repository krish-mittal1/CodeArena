import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { BookOpen, Search, Sparkles } from 'lucide-react';
import { insightsApi } from '../api/auth';

export default function Insights() {
    const navigate = useNavigate();
    const [q, setQ] = useState('');
    const { data, isLoading } = useQuery({
        queryKey: ['insights', q],
        queryFn: () => insightsApi.list({ q: q || undefined, limit: 50 }),
    });

    const items = data?.insights || [];

    return (
        <div className="min-h-screen bg-bg-root pb-16">
            <div className="max-w-3xl mx-auto px-6 py-10">
                <div className="mb-8">
                    <p className="editorial-kicker mb-1">Your mistake log</p>
                    <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
                        <Sparkles size={22} className="text-accent" />
                        AI Insight Library
                    </h1>
                    <p className="text-sm text-text-secondary mt-2">
                        Every analysis you run is saved here — patterns, fixes, and tips from your own submissions.
                    </p>
                </div>

                <div className="relative mb-6">
                    <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                    <input
                        type="search"
                        placeholder="Search problems..."
                        value={q}
                        onChange={(e) => setQ(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 bg-bg-primary border border-border text-sm"
                    />
                </div>

                {isLoading ? (
                    <p className="text-text-secondary text-sm">Loading insights...</p>
                ) : items.length === 0 ? (
                    <div className="paper-card grain-panel p-10 text-center">
                        <BookOpen size={32} className="mx-auto text-text-muted mb-3" />
                        <p className="text-text-secondary text-sm">No insights yet. Submit a practice problem and view AI analysis.</p>
                    </div>
                ) : (
                    <ul className="space-y-3">
                        {items.map((item) => (
                            <li key={item.id}>
                                <button
                                    type="button"
                                    onClick={() => navigate(`/insights/${item.id}`)}
                                    className="w-full text-left paper-card grain-panel p-4 hover:border-accent/40 transition-colors"
                                >
                                    <div className="flex justify-between items-start gap-4">
                                        <div>
                                            <p className="font-medium text-text-primary">{item.problem_title}</p>
                                            <p className="text-xs text-text-muted mt-1">{item.topic} · {item.verdict}</p>
                                        </div>
                                        <span className="text-xs text-text-muted shrink-0">
                                            {new Date(item.created_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                    {item.tip && (
                                        <p className="text-sm text-text-secondary mt-2 line-clamp-2">{item.tip}</p>
                                    )}
                                </button>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
}
