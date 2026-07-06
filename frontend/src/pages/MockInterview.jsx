import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Briefcase, Clock, Play, CheckCircle2 } from 'lucide-react';
import { mockInterviewApi } from '../api/auth';

const COMPANIES = ['Google', 'Amazon', 'Microsoft', 'Meta', 'Apple'];
const SESSION_KEY = 'codearena:mock-session';

export default function MockInterview() {
    const navigate = useNavigate();
    const [company, setCompany] = useState('Google');
    const [session, setSession] = useState(null);
    const [debrief, setDebrief] = useState(null);

    useEffect(() => {
        const raw = window.sessionStorage.getItem(SESSION_KEY);
        if (!raw) return;
        try {
            const saved = JSON.parse(raw);
            if (saved?.session_id) setSession(saved);
        } catch {
            window.sessionStorage.removeItem(SESSION_KEY);
        }
    }, []);

    const { data: liveSession } = useQuery({
        queryKey: ['mockSession', session?.session_id],
        queryFn: () => mockInterviewApi.getSession(session.session_id),
        enabled: Boolean(session?.session_id) && !debrief,
        refetchInterval: 5000,
    });

    const submissionIds = liveSession?.submission_ids || [];
    const problems = liveSession?.problems || session?.problems || [];

    const startMutation = useMutation({
        mutationFn: () => mockInterviewApi.start(company),
        onSuccess: (data) => {
            setSession(data);
            setDebrief(null);
            window.sessionStorage.setItem(SESSION_KEY, JSON.stringify(data));
            toast.success('Mock interview started — 45 minutes');
        },
        onError: () => toast.error('Could not start mock interview'),
    });

    const debriefMutation = useMutation({
        mutationFn: () => mockInterviewApi.debrief({
            session_id: session.session_id,
            submission_ids: submissionIds,
        }),
        onSuccess: (data) => {
            setDebrief(data);
            window.sessionStorage.removeItem(SESSION_KEY);
        },
        onError: () => toast.error('Could not generate debrief'),
    });

    if (debrief) {
        return (
            <div className="min-h-screen bg-bg-root px-6 py-10 max-w-2xl mx-auto">
                <h1 className="text-2xl font-bold mb-2">Mock interview debrief</h1>
                <p className={`text-lg font-semibold mb-6 ${debrief.hire_signal === 'lean_hire' ? 'text-win' : 'text-loss'}`}>
                    Signal: {debrief.hire_signal === 'lean_hire' ? 'Lean hire' : 'Keep practicing'}
                </p>
                <div className="paper-card grain-panel p-4 mb-6 text-sm space-y-2">
                    {Object.entries(debrief.rubric || {}).map(([k, v]) => (
                        <p key={k}><span className="text-text-muted capitalize">{k}:</span> {v}</p>
                    ))}
                </div>
                {debrief.problem_summaries?.length > 0 ? debrief.problem_summaries.map((s) => (
                    <div key={s.problem_title} className="paper-card grain-panel p-4 mb-4">
                        <h3 className="font-semibold">{s.problem_title}</h3>
                        <p className="text-xs text-text-muted mb-2">{s.verdict}</p>
                        <p className="text-sm text-text-secondary line-clamp-4">{s.analysis?.optimized_approach}</p>
                    </div>
                )) : (
                    <p className="text-sm text-text-secondary mb-4">No submissions were linked to this session.</p>
                )}
                <button type="button" onClick={() => navigate('/dashboard')} className="text-accent text-sm hover:underline">
                    Back to dashboard
                </button>
            </div>
        );
    }

    if (session) {
        const attemptedCount = problems.filter((p) => p.submission_id).length;
        const current = problems.find((p) => !p.submission_id) || null;
        return (
            <div className="min-h-screen bg-bg-root px-6 py-10 max-w-2xl mx-auto">
                <div className="flex items-center gap-2 text-sm text-text-muted mb-4">
                    <Clock size={16} />
                    {session.duration_minutes} min · {session.company}
                </div>
                <h1 className="text-xl font-bold mb-2">Mock interview</h1>
                <p className="text-sm text-text-secondary mb-6">
                    {attemptedCount} of {problems.length} problems submitted
                </p>
                <ul className="space-y-3 mb-8">
                    {problems.map((p, i) => (
                        <li key={p.id} className="paper-card grain-panel p-4 flex items-center justify-between gap-4">
                            <div>
                                <p className="text-xs uppercase text-text-muted mb-1">Problem {i + 1} · {p.difficulty}</p>
                                <h2 className="font-semibold">{p.title}</h2>
                            </div>
                            {p.submission_id ? (
                                <CheckCircle2 size={20} className="text-win shrink-0" />
                            ) : (
                                <button
                                    type="button"
                                    onClick={() => navigate(`/practice/${p.id}?mock=${session.session_id}`)}
                                    className="shrink-0 px-3 py-1.5 bg-accent text-white text-xs font-medium"
                                >
                                    Open
                                </button>
                            )}
                        </li>
                    ))}
                </ul>
                {current && (
                    <p className="text-xs text-text-muted mb-4">
                        AI hints and analysis are disabled during the session. Submit each problem, then return here.
                    </p>
                )}
                <button
                    type="button"
                    disabled={debriefMutation.isPending}
                    onClick={() => debriefMutation.mutate()}
                    className="px-4 py-2 border border-border text-sm hover:bg-bg-hover disabled:opacity-50"
                >
                    {debriefMutation.isPending ? 'Generating debrief...' : 'End & get AI debrief'}
                </button>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-bg-root flex items-center justify-center p-6">
            <div className="paper-card grain-panel p-8 max-w-md w-full">
                <Briefcase size={28} className="text-accent mb-4" />
                <h1 className="text-2xl font-bold mb-2">Mock interview</h1>
                <p className="text-sm text-text-secondary mb-6">
                    45-minute session: 1 easy warm-up + 1 medium. No AI during the session — full debrief after.
                </p>
                <label className="block text-sm font-medium mb-2">Target company</label>
                <select
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    className="w-full mb-6 px-3 py-2 bg-bg-primary border border-border text-sm"
                >
                    {COMPANIES.map((c) => (
                        <option key={c} value={c}>{c}</option>
                    ))}
                </select>
                <button
                    type="button"
                    disabled={startMutation.isPending}
                    onClick={() => startMutation.mutate()}
                    className="w-full flex items-center justify-center gap-2 py-3 bg-accent text-white font-semibold disabled:opacity-50"
                >
                    <Play size={16} />
                    Start mock interview
                </button>
            </div>
        </div>
    );
}
