import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useBattleStore } from '../stores/battleStore';
import { problemApi } from '../api/auth';
import TimerBar from '../components/battle/TimerBar';
import ProblemPanel from '../components/battle/ProblemPanel';
import CodeEditor from '../components/battle/CodeEditor';
import SubmissionPanel from '../components/battle/SubmissionPanel';
import MatchResultModal from '../components/battle/MatchResultModal';
import { Loader2 } from 'lucide-react';

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
            // Only reset if match is over
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
            const newLeftWidth = (e.clientX / containerWidth) * 100;
            // Constrain between 20% and 60%
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
        document.body.style.userSelect = 'none'; // prevent text selection while dragging
    };

    // Loading state
    if (!storeMatchId) {
        return (
            <div className="flex flex-col items-center justify-center h-[calc(100vh-56px)] bg-[#0e0e11] text-zinc-400 gap-4">
                <Loader2 className="w-12 h-12 text-indigo-500 animate-spin" />
                <h2 className="text-xl font-medium tracking-wide text-zinc-300">Provisioning Match Environment...</h2>
                <p className="text-sm text-zinc-500 font-mono tracking-wider">ID: {matchId}</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-screen bg-slate-950 overflow-hidden text-slate-300 antialiased selection:bg-indigo-500/30">
            {/* Timer bar — full width, top fixed */}
            <TimerBar />

            {/* Split pane body */}
            <div ref={containerRef} className="flex flex-1 overflow-hidden relative">

                {/* Left: Problem description */}
                <div
                    className="flex flex-col overflow-hidden bg-slate-950 shrink-0"
                    style={{ width: `${leftWidth}%` }}
                >
                    <ProblemPanel />
                </div>

                {/* Resizer Handle */}
                <div
                    className="w-px cursor-col-resize shrink-0 bg-slate-800 hover:bg-slate-600 active:bg-indigo-500 transition-colors z-30 group relative"
                    onMouseDown={startDrag}
                >
                    <div className="absolute inset-y-0 -left-1.5 -right-1.5" /> {/* Larger hit area */}
                </div>

                {/* Right: Editor + Submissions */}
                <div
                    className="flex flex-col flex-1 overflow-hidden bg-slate-950"
                    style={{ width: `${100 - leftWidth}%` }}
                >
                    <CodeEditor />
                    <SubmissionPanel />
                </div>
            </div>

            {/* Match result modal (overlay) */}
            <MatchResultModal />
        </div>
    );
}
