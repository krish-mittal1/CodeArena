import { useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Layers, ChevronRight } from 'lucide-react';
import { problemApi } from '../api/auth';
import { getProblemMetadata } from '../data/problemMetadata';

const TOPIC_ORDER = [
    'Arrays', 'String', 'Linked List', 'Trees', 'Binary Search',
    'Sliding Window', 'Greedy', 'Matrix', 'Dynamic Programming', 'Stack', 'Heap',
];

export default function TopicBrowse() {
    const navigate = useNavigate();
    const [params] = useSearchParams();
    const selectedTopic = params.get('topic');

    const { data: catalog = [], isLoading } = useQuery({
        queryKey: ['problem-catalog', 'dsa'],
        queryFn: () => problemApi.getCatalog({ problem_type: 'dsa' }),
    });

    const byTopic = useMemo(() => {
        const map = {};
        catalog.forEach((p) => {
            const meta = getProblemMetadata(p.title) || { topic: 'Arrays' };
            const topic = meta.topic || 'Arrays';
            if (!map[topic]) map[topic] = [];
            map[topic].push(p);
        });
        return map;
    }, [catalog]);

    const topics = [...new Set([...TOPIC_ORDER, ...Object.keys(byTopic)])].filter((t) => byTopic[t]?.length);

    if (selectedTopic) {
        const problems = byTopic[selectedTopic] || [];
        return (
            <div className="min-h-screen bg-bg-root pb-16">
                <div className="max-w-3xl mx-auto px-6 py-10">
                    <button type="button" onClick={() => navigate('/practice/dsa/topics')} className="text-sm text-text-secondary mb-4 hover:text-accent">
                        ← All topics
                    </button>
                    <h1 className="text-2xl font-bold text-text-primary mb-6">{selectedTopic}</h1>
                    <ul className="space-y-2">
                        {problems.map((p) => (
                            <li key={p.id}>
                                <button
                                    type="button"
                                    onClick={() => navigate(`/practice/${p.id}`)}
                                    className="w-full flex items-center justify-between paper-card grain-panel p-4 text-left hover:border-accent/30"
                                >
                                    <span className={p.solved ? 'text-win' : 'text-text-primary'}>{p.title}</span>
                                    <span className="text-xs text-text-muted uppercase">{p.difficulty}</span>
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-bg-root pb-16">
            <div className="max-w-4xl mx-auto px-6 py-10">
                <div className="mb-8">
                    <p className="editorial-kicker mb-1">Topic-first practice</p>
                    <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
                        <Layers size={22} className="text-accent" />
                        Browse by topic
                    </h1>
                </div>
                {isLoading ? (
                    <p className="text-text-secondary text-sm">Loading...</p>
                ) : (
                    <div className="grid gap-4 sm:grid-cols-2">
                        {topics.map((topic) => {
                            const list = byTopic[topic] || [];
                            const solved = list.filter((p) => p.solved).length;
                            return (
                                <button
                                    key={topic}
                                    type="button"
                                    onClick={() => navigate(`/practice/dsa/topics?topic=${encodeURIComponent(topic)}`)}
                                    className="paper-card grain-panel p-5 text-left hover:border-accent/30 group"
                                >
                                    <div className="flex justify-between items-center">
                                        <h2 className="font-semibold text-text-primary">{topic}</h2>
                                        <ChevronRight size={18} className="text-text-muted group-hover:text-accent" />
                                    </div>
                                    <p className="text-sm text-text-muted mt-2">{solved}/{list.length} solved</p>
                                </button>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
