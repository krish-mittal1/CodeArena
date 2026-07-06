import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Map, CheckCircle2 } from 'lucide-react';
import { problemApi, userApi } from '../api/auth';
import { STUDY_PATHS, resolvePathProgress } from '../data/studyPaths';

export default function StudyPaths() {
    const navigate = useNavigate();
    const { data: catalog = [] } = useQuery({
        queryKey: ['problem-catalog', 'dsa'],
        queryFn: () => problemApi.getCatalog({ problem_type: 'dsa' }),
    });
    const { data: progress } = useQuery({
        queryKey: ['userProgress'],
        queryFn: userApi.getProgress,
    });

    const solvedIds = progress?.solved_problem_ids || [];

    return (
        <div className="min-h-screen bg-bg-root pb-16">
            <div className="max-w-3xl mx-auto px-6 py-10">
                <div className="mb-8">
                    <p className="editorial-kicker mb-1">Curated plans</p>
                    <h1 className="text-2xl font-bold text-text-primary flex items-center gap-2">
                        <Map size={22} className="text-accent" />
                        Study paths
                    </h1>
                </div>

                <div className="space-y-6">
                    {STUDY_PATHS.map((path) => {
                        const { total, solved, pct, items } = resolvePathProgress(path, catalog, solvedIds);
                        return (
                            <div key={path.id} className="paper-card grain-panel p-6">
                                <div className="flex justify-between items-start mb-2">
                                    <div>
                                        <h2 className="text-lg font-semibold text-text-primary">{path.title}</h2>
                                        <p className="text-sm text-text-secondary mt-1">{path.description}</p>
                                    </div>
                                    <span className="text-accent font-mono text-sm">{pct}%</span>
                                </div>
                                <div className="h-2 bg-bg-surface rounded-full mb-4 overflow-hidden">
                                    <div className="h-full bg-accent" style={{ width: `${pct}%` }} />
                                </div>
                                <p className="text-xs text-text-muted mb-4">{solved}/{total} problems in catalog</p>
                                <ul className="space-y-1 max-h-48 overflow-y-auto text-sm">
                                    {items.filter((i) => i.found).slice(0, 12).map((item) => (
                                        <li key={item.title} className="flex items-center gap-2">
                                            {item.solved ? (
                                                <CheckCircle2 size={14} className="text-win shrink-0" />
                                            ) : (
                                                <span className="w-3.5 h-3.5 rounded-full border border-border shrink-0" />
                                            )}
                                            <button
                                                type="button"
                                                className="text-left hover:text-accent truncate"
                                                onClick={() => item.problem_id && navigate(`/practice/${item.problem_id}`)}
                                            >
                                                Day {item.day}: {item.title}
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
