import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useBattleStore } from '../stores/battleStore';
import { problemApi } from '../api/auth';
import TimerBar from '../components/battle/TimerBar';
import ProblemPanel from '../components/battle/ProblemPanel';
import CodeEditor from '../components/battle/CodeEditor';
import SubmissionPanel from '../components/battle/SubmissionPanel';
import MatchResultModal from '../components/battle/MatchResultModal';
import { Loader2, FileCode2, TestTube2, Settings, History } from 'lucide-react';

export default function Battle() {
    const { matchId } = useParams();
    const navigate = useNavigate();
    const storeMatchId = useBattleStore((s) => s.matchId);
    const reset = useBattleStore((s) => s.reset);
    const problemId = useBattleStore((s) => s.problemId);
    const problem = useBattleStore((s) => s.problem);
    const setProblem = useBattleStore((s) => s.setProblem);

    // Resizable pane state
    const containerRef = useRef(null);
    const [leftWidth, setLeftWidth] = useState(45); // percentage
    const isDragging = useRef(false);

    // If user navigates directly without match data, redirect back to dashboard
    useEffect(() => {
        if (!storeMatchId && matchId) {
            const timer = setTimeout(() => {
                if (!useBattleStore.getState().matchId) {
                    navigate('/dashboard', { replace: true });
                }
            }, 3000);
            return () => clearTimeout(timer);
        }
    }, [storeMatchId, matchId, navigate]);

    // Fetch full problem details once we know the problemId
    useEffect(() => {
        if (!storeMatchId || !problemId) return;
        if (problem && problem.description) return;

        let cancelled = false;
        (async () => {
            try {
                const data = await problemApi.getById(problemId);
                if (cancelled) return;

                const examples = Array.isArray(data.sample_cases)
                    ? data.sample_cases.map((tc) => ({
                        input: tc.input,
                        output: tc.expected_output,
                    }))
                    : [];

                setProblem({
                    id: data.id,
                    title: data.title,
                    description: data.description,
                    difficulty: data.difficulty,
                    input_format: data.input_format,
                    output_format: data.output_format,
                    constraints: data.constraints,
                    time_limit_ms: data.time_limit_ms,
                    memory_limit_mb: data.memory_limit_mb,
                    examples,
                });
            } catch (e) {
                console.error('Failed to load problem details:', e);
            }
        })();

        return () => {
            cancelled = true;
        };
    }, [storeMatchId, problemId, problem, setProblem]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (useBattleStore.getState().matchResult) {
                reset();
            }
        };
    }, [reset]);

    // Resizer logic
    useEffect(() => {
        const handleMouseMove = (e) => {
            if (!isDragging.current || !containerRef.current) return;
            const containerWidth = containerRef.current.getBoundingClientRect().width;

            // Adjust for the 48px activity bar width
            const newLeftWidth = ((e.clientX - 48) / containerWidth) * 100;
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

    // Loading state
    if (!storeMatchId) {
        return (
            <div className="flex flex-col items-center justify-center h-[calc(100vh-56px)] bg-bg-root text-text-secondary gap-4">
                <Loader2 className="w-12 h-12 text-accent animate-spin" />
                <h2 className="text-xl font-medium tracking-wide text-text-primary">Provisioning Match Environment...</h2>
                <p className="text-sm text-text-muted font-mono tracking-wider">ID: {matchId}</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-screen bg-bg-root text-text-primary antialiased overflow-hidden">
            {/* Top Navigation Bar / Actions */}
            <TimerBar />

            {/* Main Application Body */}
            <div className="flex flex-1 overflow-hidden relative">

                {/* IDE-like Activity Bar (Leftmost) */}
                <div className="w-12 bg-bg-primary border-r border-border shrink-0 flex flex-col items-center py-4 gap-6 z-10 selection:bg-transparent">
                    <button className="text-text-primary relative group focus:outline-none" title="Problem Description">
                        <div className="absolute -left-3 top-0 bottom-0 w-[2px] bg-accent"></div>
                        <FileCode2 className="w-6 h-6 opacity-100" />
                    </button>
                    <button className="text-text-muted hover:text-text-primary transition-colors focus:outline-none" title="Test Cases">
                        <TestTube2 className="w-6 h-6" />
                    </button>
                    <button className="text-text-muted hover:text-text-primary transition-colors focus:outline-none" title="Submission History">
                        <History className="w-6 h-6" />
                    </button>
                    <div className="flex-1"></div>
                    <button className="text-text-muted hover:text-text-primary transition-colors focus:outline-none" title="Settings">
                        <Settings className="w-6 h-6" />
                    </button>
                </div>

                {/* Left: Problem Details Pane */}
                <div
                    className="flex flex-col overflow-hidden bg-bg-root shrink-0"
                    style={{ width: `calc(${leftWidth}% - 48px)` }}
                >
                    <ProblemPanel />
                </div>

                {/* Resizer Handle (Flat Design) */}
                <div
                    ref={containerRef}
                    className="w-px cursor-col-resize shrink-0 bg-border hover:bg-accent active:bg-accent transition-colors z-30 group relative"
                    onMouseDown={startDrag}
                >
                    <div className="absolute inset-y-0 -left-1 -right-1" />
                </div>

                {/* Right: Code Editor & Execution Panel */}
                <div
                    className="flex flex-col flex-1 overflow-hidden bg-bg-root"
                >
                    <CodeEditor />
                    <SubmissionPanel />
                </div>
            </div>

            {/* Modals */}
            <MatchResultModal />
        </div>
    );
}
