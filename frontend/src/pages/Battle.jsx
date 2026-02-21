/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Battle Page — full split-pane layout
   
   Layout:
     TimerBar (full width)
     ┌──────────┬──────────────────┐
     │ Problem  │ CodeEditor       │
     │ Panel    │                  │
     │          ├──────────────────┤
     │          │ SubmissionPanel  │
     └──────────┴──────────────────┘
     MatchResultModal (overlay when match ends)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useBattleStore } from '../stores/battleStore';
import { problemApi } from '../api/auth';
import TimerBar from '../components/battle/TimerBar';
import ProblemPanel from '../components/battle/ProblemPanel';
import CodeEditor from '../components/battle/CodeEditor';
import SubmissionPanel from '../components/battle/SubmissionPanel';
import MatchResultModal from '../components/battle/MatchResultModal';
import styles from '../styles/battle.module.css';

export default function Battle() {
    const { matchId } = useParams();
    const navigate = useNavigate();
    const storeMatchId = useBattleStore((s) => s.matchId);
    const reset = useBattleStore((s) => s.reset);
    const problemId = useBattleStore((s) => s.problemId);
    const problem = useBattleStore((s) => s.problem);
    const setProblem = useBattleStore((s) => s.setProblem);

    // If user navigates directly to /battle/:id without match data, redirect
    useEffect(() => {
        if (!storeMatchId && matchId) {
            // Could be a reconnection — for now redirect to dashboard
            // TODO: add API call to fetch match state on direct nav
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

    // Loading state
    if (!storeMatchId) {
        return (
            <div className={styles.battlePage}>
                <div className={styles.loading}>
                    <div className={styles.loadingIcon}>⚔</div>
                    <div className={styles.loadingText}>Joining match...</div>
                    <div className={styles.loadingSub}>
                        Match ID: {matchId}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={styles.battlePage}>
            {/* Timer bar — full width */}
            <TimerBar />

            {/* Split pane body */}
            <div className={styles.battleBody}>
                {/* Left: Problem description */}
                <div className={styles.leftPane}>
                    <ProblemPanel />
                </div>

                <div className={styles.resizeHandle} />

                {/* Right: Editor + Submissions */}
                <div className={styles.rightPane}>
                    <CodeEditor />
                    <SubmissionPanel />
                </div>
            </div>

            {/* Match result modal (overlay) */}
            <MatchResultModal />
        </div>
    );
}
