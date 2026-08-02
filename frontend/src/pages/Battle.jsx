import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useBattleStore } from '../stores/battleStore';
import { useAuthStore } from '../stores/authStore';
import { problemApi, matchApi } from '../api/auth';
import TimerBar from '../components/battle/TimerBar';
import ProblemPanel from '../components/battle/ProblemPanel';
import CodeEditor from '../components/battle/CodeEditor';
import SubmissionPanel from '../components/battle/SubmissionPanel';
import MatchResultModal from '../components/battle/MatchResultModal';
import { Loader2, FileCode2, Code2, TestTube2, Settings, History } from 'lucide-react';

function mapProblemPayload(data) {
    const examples = Array.isArray(data.examples) && data.examples.length > 0
        ? data.examples.map((ex) => ({
            input: ex.input,
            output: ex.output,
            explanation: ex.explanation || null,
        }))
        : Array.isArray(data.sample_cases)
            ? data.sample_cases.map((tc) => ({
                input: tc.input,
                output: tc.expected_output,
                explanation: tc.explanation || null,
            }))
            : [];

    return {
        id: data.id,
        title: data.title,
        description: data.description,
        difficulty: data.difficulty,
        input_format: data.input_format,
        output_format: data.output_format,
        constraints: data.constraints,
        time_limit_ms: data.time_limit_ms,
        memory_limit_mb: data.memory_limit_mb,
        method_name: data.method_name,
        parameters: data.parameters,
        return_type: data.return_type,
        sample_cases: data.sample_cases || [],
        examples,
        images: Array.isArray(data.images) ? data.images : [],
    };
}

export default function Battle() {
    const { matchId } = useParams();
    const navigate = useNavigate();
    const storeMatchId = useBattleStore((s) => s.matchId);
    const reset = useBattleStore((s) => s.reset);
    const setMatch = useBattleStore((s) => s.setMatch);
    const problemId = useBattleStore((s) => s.problemId);
    const problem = useBattleStore((s) => s.problem);
    const problems = useBattleStore((s) => s.problems);
    const problemDetails = useBattleStore((s) => s.problemDetails);
    const setProblem = useBattleStore((s) => s.setProblem);
    const [hydrateFailed, setHydrateFailed] = useState(false);
    const [mobileTab, setMobileTab] = useState('code'); // problem | code

    const containerRef = useRef(null);
    const [leftWidth, setLeftWidth] = useState(45);
    const isDragging = useRef(false);

    useEffect(() => {
        if (storeMatchId || !matchId) return;

        let cancelled = false;
        (async () => {
            try {
                const data = await matchApi.getMatch(matchId);
                if (cancelled || useBattleStore.getState().matchId) return;

                const currentUserId = useAuthStore.getState().user?.id;
                const p1 = data.player1;
                const p2 = data.player2;
                let opponent = null;
                if (p1 && p2) {
                    const p1Id = String(p1.id);
                    const p2Id = String(p2.id);
                    const me = String(currentUserId);
                    if (p1Id === me) {
                        opponent = { user_id: p2Id, username: p2.username, elo: p2.elo };
                    } else {
                        opponent = { user_id: p1Id, username: p1.username, elo: p1.elo };
                    }
                }

                let remaining = data.duration_seconds || 1800;
                if (data.started_at) {
                    const started = new Date(data.started_at).getTime();
                    const elapsed = Math.floor((Date.now() - started) / 1000);
                    remaining = Math.max(0, (data.duration_seconds || 1800) - elapsed);
                }

                setMatch({
                    match_id: String(data.id),
                    problem_id: data.problem_id ? String(data.problem_id) : null,
                    problems: data.problems || [],
                    solved_problem_ids: data.solved_problem_ids || [],
                    opponent,
                    duration_seconds: data.duration_seconds || 1800,
                    remaining_seconds: remaining,
                });
            } catch (e) {
                console.error('Failed to hydrate match:', e);
                if (!cancelled) setHydrateFailed(true);
            }
        })();

        return () => {
            cancelled = true;
        };
    }, [storeMatchId, matchId, setMatch]);

    useEffect(() => {
        if (storeMatchId || !matchId) return;
        if (!hydrateFailed) {
            const timer = setTimeout(() => {
                if (!useBattleStore.getState().matchId) {
                    navigate('/dashboard', { replace: true });
                }
            }, 5000);
            return () => clearTimeout(timer);
        }
        navigate('/dashboard', { replace: true });
    }, [storeMatchId, matchId, navigate, hydrateFailed]);

    // Load details for every match problem (and active problem fallback)
    useEffect(() => {
        if (!storeMatchId) return;
        const ids = problems.length
            ? problems.map((p) => p.id)
            : (problemId ? [problemId] : []);
        if (!ids.length) return;

        let cancelled = false;
        (async () => {
            for (const id of ids) {
                if (cancelled) return;
                const existing = useBattleStore.getState().problemDetails[id];
                if (existing?.description) continue;
                try {
                    const data = await problemApi.getById(id);
                    if (cancelled) return;
                    setProblem(mapProblemPayload(data));
                } catch (e) {
                    console.error('Failed to load problem details:', e);
                }
            }
        })();

        return () => {
            cancelled = true;
        };
    }, [storeMatchId, problems, problemId, setProblem]);

    // Ensure active problem object is synced when details arrive
    useEffect(() => {
        if (!problemId) return;
        const details = problemDetails[problemId];
        if (details && (!problem || problem.id !== details.id || !problem.description)) {
            setProblem(details);
        }
    }, [problemId, problemDetails, problem, setProblem]);

    useEffect(() => {
        return () => {
            const { matchId: activeId, matchResult } = useBattleStore.getState();
            if (activeId && !matchResult) {
                return;
            }
            reset();
        };
    }, [reset]);

    useEffect(() => {
        const handleMouseMove = (e) => {
            if (!isDragging.current || !containerRef.current) return;
            const rect = containerRef.current.getBoundingClientRect();
            const activityBarWidth = 48;
            const usableWidth = rect.width - activityBarWidth;

            const newLeftWidth = ((e.clientX - rect.left - activityBarWidth) / usableWidth) * 100;
            if (newLeftWidth >= 20 && newLeftWidth <= 60) {
                setLeftWidth(newLeftWidth);
            }
        };

        const handleMouseUp = () => {
            if (isDragging.current) {
                isDragging.current = false;
                document.body.style.cursor = 'default';
                document.body.style.userSelect = 'auto';
            }
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }, []);

    const startDrag = () => {
        isDragging.current = true;
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    };

    if (!storeMatchId) {
        return (
            <div className="flex flex-col items-center justify-center h-[calc(100dvh-64px)] bg-bg-root text-text-secondary gap-4 px-4 text-center">
                <Loader2 className="w-12 h-12 text-accent animate-spin" />
                <h2 className="text-lg sm:text-xl font-medium tracking-[-0.03em] text-text-primary">Provisioning Match Environment...</h2>
                <p className="text-sm text-text-muted font-mono tracking-wider break-all">ID: {matchId}</p>
            </div>
        );
    }

    const showProblem = mobileTab === 'problem';
    const showCode = mobileTab === 'code';

    return (
        <div className="battle-page flex flex-col h-[calc(100dvh-64px)] bg-bg-root text-text-primary antialiased overflow-hidden">
            <TimerBar />

            <div className="md:hidden flex shrink-0 border-b border-border bg-bg-primary">
                <button
                    type="button"
                    onClick={() => setMobileTab('problem')}
                    className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-semibold min-h-[44px] transition-colors ${
                        showProblem
                            ? 'text-text-primary border-b-2 border-accent'
                            : 'text-text-muted'
                    }`}
                >
                    <FileCode2 className="w-4 h-4" />
                    Problem
                </button>
                <button
                    type="button"
                    onClick={() => setMobileTab('code')}
                    className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-semibold min-h-[44px] transition-colors ${
                        showCode
                            ? 'text-text-primary border-b-2 border-accent'
                            : 'text-text-muted'
                    }`}
                >
                    <Code2 className="w-4 h-4" />
                    Code
                </button>
            </div>

            <div ref={containerRef} className="flex flex-1 overflow-hidden relative min-h-0">
                <div className="hidden md:flex w-12 bg-bg-primary border-r border-border shrink-0 flex-col items-center py-4 gap-6 z-10 selection:bg-transparent shadow-[6px_0_16px_rgba(0,0,0,0.12)]">
                    <button type="button" className="text-text-primary relative group focus:outline-none" title="Problem Description">
                        <div className="absolute -left-3 top-0 bottom-0 w-[2px] bg-accent" />
                        <FileCode2 className="w-6 h-6 opacity-100" />
                    </button>
                    <button type="button" className="text-text-muted hover:text-text-primary transition-colors focus:outline-none" title="Test Cases">
                        <TestTube2 className="w-6 h-6" />
                    </button>
                    <button type="button" className="text-text-muted hover:text-text-primary transition-colors focus:outline-none" title="Submission History">
                        <History className="w-6 h-6" />
                    </button>
                    <div className="flex-1" />
                    <button type="button" className="text-text-muted hover:text-text-primary transition-colors focus:outline-none" title="Settings">
                        <Settings className="w-6 h-6" />
                    </button>
                </div>

                <div
                    className={`battle-problem-pane flex flex-col overflow-hidden bg-bg-root shrink-0 min-h-0 ${
                        !showProblem ? 'max-md:hidden' : ''
                    }`}
                    style={{ width: `calc(${leftWidth}% - 48px)` }}
                >
                    <ProblemPanel />
                </div>

                <div
                    className="hidden md:block w-px cursor-col-resize shrink-0 bg-border hover:bg-accent active:bg-accent transition-colors z-30 group relative"
                    onMouseDown={startDrag}
                >
                    <div className="absolute inset-y-0 -left-1 -right-1" />
                </div>

                <div
                    className={`flex flex-col flex-1 overflow-hidden bg-bg-root min-h-0 min-w-0 ${
                        !showCode ? 'max-md:hidden' : ''
                    }`}
                >
                    <CodeEditor />
                    <SubmissionPanel />
                </div>
            </div>

            <MatchResultModal />
        </div>
    );
}
