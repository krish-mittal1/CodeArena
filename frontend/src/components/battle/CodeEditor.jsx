import { useCallback } from 'react';
import dynamic from 'next/dynamic';
import toast from 'react-hot-toast';
import { useBattleStore } from '../../stores/battleStore';
import { practiceApi, submissionApi } from '../../api/auth';
import { LANGUAGES, CODE_TEMPLATES, generateBoilerplate } from '../../utils/constants';
import { defineCodeArenaTheme, CODEARENA_THEME_NAME } from '../../utils/editorTheme';
import { Code2, Play, RotateCcw, Settings2 } from 'lucide-react';

const Editor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

export default function CodeEditor() {
    const language = useBattleStore((s) => s.language);
    const code = useBattleStore((s) => s.code);
    const matchId = useBattleStore((s) => s.matchId);
    const problem = useBattleStore((s) => s.problem);
    const submissionStatus = useBattleStore((s) => s.submissionStatus);
    const runStatus = useBattleStore((s) => s.runStatus);
    const matchResult = useBattleStore((s) => s.matchResult);

    const setLanguage = useBattleStore((s) => s.setLanguage);
    const setCode = useBattleStore((s) => s.setCode);
    const setSubmissionStatus = useBattleStore((s) => s.setSubmissionStatus);
    const setRunStatus = useBattleStore((s) => s.setRunStatus);
    const setRunResult = useBattleStore((s) => s.setRunResult);

    const monacoLang = LANGUAGES.find((l) => l.id === language)?.monacoId || 'python';

    const handleEditorWillMount = useCallback((monaco) => {
        defineCodeArenaTheme(monaco);
    }, []);

    const remainingSeconds = useBattleStore((s) => s.remainingSeconds);

    const isSubmitting = submissionStatus === 'submitting' || submissionStatus === 'running';
    const isRunningSamples = runStatus === 'running';
    const canAct = !isSubmitting && !isRunningSamples && !matchResult && code.trim().length > 0 && remainingSeconds > 0;

    const handleRun = async () => {
        if (!canAct || !problem) return;

        setRunStatus('running');
        setRunResult({
            status: 'running',
            passed_test_cases: 0,
            total_test_cases: problem.sample_cases?.length || 0,
            cases: [],
        });
        try {
            // Samples only via practice run API — never hidden tests.
            const data = await practiceApi.run({
                problem_id: problem.id,
                language,
                code,
            });
            setRunResult(data);
        } catch (err) {
            console.error('Sample run failed:', err);
            const msg = err.response?.data?.detail || err.message || 'Run failed';
            toast.error(typeof msg === 'string' ? msg : 'Run failed');
            setRunResult({
                status: 'error',
                passed_test_cases: 0,
                total_test_cases: 0,
                execution_time_ms: 0,
                memory_used_kb: 0,
                cases: [],
                message: typeof msg === 'string' ? msg : 'Run failed',
            });
        }
    };

    const handleSubmit = async () => {
        if (!canAct || !matchId || !problem) return;

        setSubmissionStatus('submitting');
        try {
            await submissionApi.submit({
                match_id: matchId,
                problem_id: problem.id,
                language,
                code,
            });
            setSubmissionStatus('running');
        } catch (err) {
            console.error('Submit failed:', err);
            const msg = err.response?.data?.detail || err.message || 'Submit failed';
            toast.error(typeof msg === 'string' ? msg : 'Submit failed');
            setSubmissionStatus('idle');
        }
    };

    const handleReset = () => {
        setCode(generateBoilerplate(language, problem) || CODE_TEMPLATES[language] || '');
    };

    return (
        <div className="flex flex-col flex-1 h-full bg-bg-root overflow-hidden relative">
            <div className="flex items-center justify-between gap-2 px-3 sm:px-4 py-2 bg-bg-primary border-b border-border shrink-0 z-10">
                <div className="flex items-center gap-2 sm:gap-4 min-w-0">
                    <div className="hidden sm:flex items-center gap-2">
                        <Code2 className="w-4 h-4 text-text-secondary" />
                        <span className="text-xs font-semibold tracking-wide text-text-primary">editor</span>
                    </div>

                    <div className="relative group">
                        <select
                            className="appearance-none bg-bg-surface border border-border hover:border-text-muted text-text-primary text-xs font-medium rounded-sm px-3 py-2 sm:py-1 pr-7 outline-none focus:border-accent transition-all cursor-pointer min-h-[36px]"
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                            disabled={!!matchResult}
                        >
                            {LANGUAGES.map((lang) => (
                                <option key={lang.id} value={lang.id} className="bg-bg-primary text-text-primary">
                                    {lang.label}
                                </option>
                            ))}
                        </select>
                        <Settings2 className="w-3 h-3 text-text-muted absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none group-hover:text-text-secondary transition-colors" />
                    </div>
                </div>

                <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
                    <button
                        onClick={handleReset}
                        disabled={!!matchResult}
                        className="flex items-center gap-1.5 px-2.5 sm:px-3 py-2 sm:py-1 min-h-[36px] rounded-sm text-xs font-medium text-text-secondary hover:text-text-primary hover:bg-bg-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Reset to template"
                    >
                        <RotateCcw className="w-3.5 h-3.5" />
                        <span className="hidden sm:inline">Reset</span>
                    </button>
                    <button
                        onClick={handleRun}
                        disabled={!canAct}
                        className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-2 sm:py-1 min-h-[36px] rounded-sm text-xs font-bold transition-all ${
                            canAct
                                ? 'bg-bg-surface hover:bg-bg-hover text-text-primary border border-border'
                                : 'bg-bg-surface border border-border text-text-muted cursor-not-allowed'
                        }`}
                        title="Run against sample cases only"
                    >
                        {isRunningSamples ? (
                            <>
                                <span className="w-3.5 h-3.5 border-2 border-text-muted/30 border-t-text-primary rounded-full animate-spin" />
                                <span className="hidden sm:inline">Running</span>
                            </>
                        ) : (
                            <>
                                <Play className="w-3.5 h-3.5" />
                                <span className="hidden sm:inline">Run</span>
                            </>
                        )}
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={!canAct}
                        className={`flex items-center gap-1.5 px-3 sm:px-4 py-2 sm:py-1 min-h-[36px] rounded-sm text-xs font-bold transition-all ${
                            canAct
                                ? 'bg-win hover:bg-win/90 text-white'
                                : 'bg-bg-surface border border-border text-text-muted cursor-not-allowed'
                        }`}
                    >
                        {isSubmitting ? (
                            <>
                                <span className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                                Running
                            </>
                        ) : (
                            <>
                                <Play className="w-3.5 h-3.5 fill-current" />
                                Submit
                            </>
                        )}
                    </button>
                </div>
            </div>

            <div className="flex-1 w-full bg-bg-root relative">
                <Editor
                    height="100%"
                    language={monacoLang}
                    value={code}
                    onChange={(value) => setCode(value || '')}
                    theme={CODEARENA_THEME_NAME}
                    beforeMount={handleEditorWillMount}
                    options={{
                        fontSize: 13,
                        fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
                        minimap: { enabled: false },
                        scrollBeyondLastLine: false,
                        padding: { top: 12, bottom: 12 },
                        lineNumbers: 'on',
                        renderLineHighlight: 'line',
                        cursorBlinking: 'smooth',
                        smoothScrolling: true,
                        wordWrap: 'on',
                        tabSize: 4,
                        readOnly: !!matchResult,
                        automaticLayout: true,
                        scrollbar: {
                            verticalScrollbarSize: 10,
                            horizontalScrollbarSize: 10,
                        },
                    }}
                />
            </div>
        </div>
    );
}
