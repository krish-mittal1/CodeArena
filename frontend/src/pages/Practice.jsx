import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import confetti from 'canvas-confetti';
import {
    ArrowLeft, Code2, Play, RotateCcw, Settings2,
    CheckCircle2, XCircle, Clock, AlertTriangle, Sparkles,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { problemApi, practiceApi, mockInterviewApi } from '../api/auth';
import { LANGUAGES, CODE_TEMPLATES, VERDICTS, generateBoilerplate } from '../utils/constants';
import { defineCodeArenaTheme, CODEARENA_THEME_NAME } from '../utils/editorTheme';
import Badge from '../components/ui/Badge';
import AIAnalysisPanel from '../components/ui/AIAnalysisPanel';
import ResizableSplit from '../components/ui/ResizableSplit';

const Editor = dynamic(() => import('@monaco-editor/react'), { ssr: false });


const STATUS_ICONS = {
    accepted: CheckCircle2,
    wrong_answer: XCircle,
    tle: Clock,
    mle: AlertTriangle,
    runtime_error: AlertTriangle,
    compilation_error: AlertTriangle,
};

export default function Practice() {
    const { problemId } = useParams();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const mockSessionId = searchParams.get('mock');
    const isMockMode = Boolean(mockSessionId);
    const queryClient = useQueryClient();
    const [language, setLanguage] = useState('cpp');
    const [code, setCode] = useState('');
    const [verdict, setVerdict] = useState(null);
    const [runResult, setRunResult] = useState(null);
    const [polling, setPolling] = useState(false);
    const [submissionId, setSubmissionId] = useState(null);

    // AI Analysis state
    const [aiAnalysis, setAiAnalysis] = useState(null);
    const [showAIPanel, setShowAIPanel] = useState(false);
    const [aiLoading, setAiLoading] = useState(false);
    const [shareSlug, setShareSlug] = useState(null);
    const [hintText, setHintText] = useState(null);
    const [hintLoading, setHintLoading] = useState(false);
    const codeLoadedRef = useRef('');

    // Monaco custom theme
    const handleEditorWillMount = useCallback((monaco) => {
        defineCodeArenaTheme(monaco);
    }, []);

    // Confetti on accepted
    const prevVerdictRef = useRef(null);
    useEffect(() => {
        if (verdict?.status === 'accepted' && prevVerdictRef.current !== 'accepted') {
            confetti({
                particleCount: 80,
                spread: 70,
                origin: { y: 0.7 },
                colors: ['#c96d3a', '#dcc080', '#a3c47a', '#7ec4cf', '#f1e6d4'],
                disableForReducedMotion: true,
            });
        }
        prevVerdictRef.current = verdict?.status || null;
    }, [verdict?.status]);

    const { data: problem, isLoading } = useQuery({
        queryKey: ['problem', problemId],
        queryFn: () => problemApi.getById(problemId),
        enabled: !!problemId,
    });
    const isCompetitiveProblem = problem?.problem_type === 'cp';
    const practiceBackPath = isCompetitiveProblem ? '/practice/competitive' : '/practice/dsa';
    const generatedBoilerplate = useMemo(
        () => (problem ? (generateBoilerplate(language, problem) || CODE_TEMPLATES[language] || '') : (CODE_TEMPLATES[language] || '')),
        [language, problem]
    );
    const draftKey = useMemo(
        () => (problemId ? `codearena:draft:${problemId}:${language}` : ''),
        [problemId, language]
    );

    // One-time cleanup: purge all stale drafts so correct templates load fresh
    useEffect(() => {
        const cleanupDone = window.sessionStorage.getItem('codearena:drafts-cleaned-v2');
        if (cleanupDone) return;
        const keysToRemove = [];
        for (let i = 0; i < window.localStorage.length; i++) {
            const key = window.localStorage.key(i);
            if (key && key.startsWith('codearena:draft:')) {
                keysToRemove.push(key);
            }
        }
        keysToRemove.forEach((k) => window.localStorage.removeItem(k));
        window.sessionStorage.setItem('codearena:drafts-cleaned-v2', '1');
    }, []);

    // Load saved draft or boilerplate when problem/language changes
    useEffect(() => {
        if (!problem || !draftKey) return;
        const savedDraft = window.localStorage.getItem(draftKey);
        const nextCode = savedDraft ?? generatedBoilerplate;
        codeLoadedRef.current = nextCode;
        setCode(nextCode);
    }, [problemId, language, draftKey, generatedBoilerplate, problem]);

    useEffect(() => {
        if (!draftKey || !problem) return;
        if (code === codeLoadedRef.current) return;
        if (!code) return;
        window.localStorage.setItem(draftKey, code);
    }, [code, draftKey, problem]);

    const { data: history = [], refetch: refetchHistory } = useQuery({
        queryKey: ['practiceHistory', problemId],
        queryFn: () => practiceApi.getSubmissions(problemId),
        enabled: !!problemId,
    });

    const monacoLang = LANGUAGES.find((l) => l.id === language)?.monacoId || 'python';

    const aiAnalysisInProgress = useRef(false);

    // Auto-trigger AI analysis when verdict is finalized
    const triggerAIAnalysis = async (sub) => {
        if (!sub?.id || !problemId || aiLoading || aiAnalysisInProgress.current) return;
        aiAnalysisInProgress.current = true;
        setAiLoading(true);
        setAiAnalysis(null);
        setShowAIPanel(true);
        try {
            const result = await practiceApi.analyze({
                submission_id: sub.id,
                problem_id: problemId,
            });
            setAiAnalysis(result);
            if (result.share_slug) setShareSlug(result.share_slug);
        } catch (err) {
            console.error('AI analysis failed:', err);
            setAiAnalysis({
                problem_concept: 'The core idea could not be generated right now.',
                verdict_explanation: 'AI analysis could not be completed at this time.',
                submitted_approach: 'Your approach summary is not available right now.',
                time_complexity: 'N/A',
                space_complexity: 'N/A',
                worst_approach: 'Try starting from the brute-force version first, then improve it.',
                worst_time_complexity: 'N/A',
                worst_space_complexity: 'N/A',
                issues: [],
                failed_test_explanation: '',
                optimized_approach: 'Please try again later.',
                optimized_time_complexity: 'N/A',
                optimized_space_complexity: 'N/A',
                alternative_approaches: [],
                improved_code: '',
                tips: [],
            });
        } finally {
            setAiLoading(false);
            aiAnalysisInProgress.current = false;
        }
    };

    const submitMutation = useMutation({
        mutationFn: (data) => practiceApi.submit(data),
        onSuccess: (data) => {
            setSubmissionId(data.id);
            setPolling(true);
            setVerdict({ status: 'running', passed_test_cases: 0, total_test_cases: data.total_test_cases });
        },
        onError: (err) => {
            setVerdict({ status: 'error', message: err.response?.data?.detail || 'Submission failed' });
        },
    });

    const runMutation = useMutation({
        mutationFn: (data) => practiceApi.run(data),
        onSuccess: (data) => {
            setRunResult(data);
        },
        onError: (err) => {
            setRunResult({
                status: 'error',
                passed_test_cases: 0,
                total_test_cases: 0,
                execution_time_ms: 0,
                memory_used_kb: 0,
                cases: [],
                message: err.response?.data?.detail || 'Run failed',
            });
        },
    });

    // Poll for results
    useEffect(() => {
        if (!polling || !submissionId) return;

        const interval = setInterval(async () => {
            try {
                const subs = await practiceApi.getSubmissions(problemId);
                const sub = subs.find((s) => s.id === submissionId);
                if (sub && sub.status !== 'queued' && sub.status !== 'running') {
                    setVerdict(sub);
                    setPolling(false);
                    refetchHistory();
                    if (sub.status === 'accepted') {
                        queryClient.setQueryData(['problem', problemId], (current) =>
                            current ? { ...current, solved: true } : current
                        );
                        queryClient.invalidateQueries({ queryKey: ['problems'] });
                        practiceApi.recordSolve(problemId).catch(() => {});
                    }
                    if (isMockMode && mockSessionId) {
                        mockInterviewApi.recordSubmission(mockSessionId, problemId, sub.id).catch(() => {});
                        toast.success('Submission recorded — return to mock interview when ready', { duration: 4000 });
                    } else if (!isCompetitiveProblem) {
                        triggerAIAnalysis(sub);
                    }
                } else if (sub) {
                    setVerdict(sub);
                }
            } catch {
                // ignore polling errors
            }
        }, 1500);

        return () => clearInterval(interval);
    }, [polling, submissionId, problemId, queryClient, refetchHistory, isCompetitiveProblem, isMockMode, mockSessionId]);

    const handleHint = async (level) => {
        if (!problemId || hintLoading) return;
        setHintLoading(true);
        try {
            const res = await practiceApi.getHint({ problem_id: problemId, hint_level: level });
            setHintText(res.content);
        } catch (err) {
            const detail = err.response?.data?.detail;
            const message = typeof detail === 'string'
                ? detail
                : err.response?.status === 429
                    ? 'Daily hint limit reached for this problem. Try again tomorrow.'
                    : 'Hint unavailable right now. Please try again.';
            setHintText(message);
        } finally {
            setHintLoading(false);
        }
    };

    const handleShareInsight = () => {
        if (!shareSlug) return;
        const url = `${window.location.origin}/insight/${shareSlug}`;
        navigator.clipboard.writeText(url).then(
            () => toast.success('Insight link copied'),
            () => toast.error('Could not copy'),
        );
    };

    const handleSubmit = () => {
        if (submitMutation.isPending || !code.trim()) return;
        setVerdict(null);
        setRunResult(null);
        setAiAnalysis(null);
        setShowAIPanel(false);
        submitMutation.mutate({
            problem_id: problemId,
            language,
            code,
        });
    };

    const handleRun = () => {
        if (runMutation.isPending || submitMutation.isPending || polling || !code.trim()) return;
        setRunResult({ status: 'running', passed_test_cases: 0, total_test_cases: problem.sample_cases?.length || 0, cases: [] });
        runMutation.mutate({
            problem_id: problemId,
            language,
            code,
        });
    };

    const handleReset = () => {
        const nextCode = generatedBoilerplate;
        if (draftKey) {
            window.localStorage.removeItem(draftKey);
        }
        codeLoadedRef.current = nextCode;
        setCode(nextCode);
        setVerdict(null);
    };

    const handleLanguageChange = (newLang) => {
        setLanguage(newLang);
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-bg-root flex items-center justify-center">
                <div className="text-center">
                    <div className="w-12 h-12 rounded-[16px_12px_14px_10px] bg-accent/10 flex items-center justify-center mx-auto mb-3 animate-pulse shadow-[2px_2px_0_rgba(0,0,0,0.12)]">
                        <Code2 size={22} className="text-accent" />
                    </div>
                    <p className="text-text-secondary text-sm">Loading problem...</p>
                </div>
            </div>
        );
    }

    if (!problem) {
        return (
            <div className="min-h-screen bg-bg-root flex items-center justify-center">
                <p className="text-text-secondary">Problem not found</p>
            </div>
        );
    }

    const verdictInfo = verdict ? VERDICTS[verdict.status] : null;
    const StatusIcon = verdict ? STATUS_ICONS[verdict.status] : null;
    const renderCodeforcesTextBlock = (content) => (
        <div className="text-sm text-text-secondary leading-7 whitespace-pre-wrap">
            {content}
        </div>
    );

    const normalizeLeetCodeText = (content) => {
        if (!content) return '';
        return String(content)
            .replace(/JSON array/gi, 'array')
            .replace(/\bint\[\]\[\]\b/g, '2D integer array')
            .replace(/\bint\[\]\b/g, 'integer array')
            .replace(/\bstring\[\]\[\]\b/g, '2D string array')
            .replace(/\bstring\[\]\b/g, 'string array')
            .replace(/\bstr\[\]\b/g, 'string array')
            .replace(/\bstr\b/g, 'string')
            .replace(/\bbool\b/gi, 'boolean')
            .replace(/\s+\((?:int|string|boolean|bool|float|double|long)(?:\[\])?(?:\[\])?\)/g, '')
            .trim();
    };

    const formatDsaSampleInput = (sampleCase) => {
        const lines = (sampleCase?.input || '').split('\n').filter((line) => line.trim().length > 0);
        if (!problem?.parameters?.length) return sampleCase?.input || '';
        return lines.map((line, index) => {
            const param = problem.parameters[index];
            if (!param) return line;
            return `${param.name} = ${line}`;
        }).join('\n');
    };

    const formatDsaSampleOutput = (sampleCase) => {
        if (!sampleCase) return '';
        if (problem?.return_type === 'boolean' || problem?.return_type === 'bool') {
            return String(sampleCase.expected_output).toLowerCase();
        }
        return sampleCase.expected_output || '';
    };

    const formatCodeforcesExamples = (sampleCases) => (
        <div className="space-y-4">
            {sampleCases.map((tc, i) => (
                <div key={i} className="border border-border bg-bg-primary overflow-hidden rounded-[6px]">
                    {sampleCases.length > 1 && (
                        <div className="px-3 py-2 border-b border-border bg-bg-surface/60">
                            <p className="text-sm font-semibold text-text-primary">{`Example ${i + 1}`}</p>
                        </div>
                    )}
                    <div className="border-t border-border">
                        <div className="px-2.5 py-1 bg-bg-surface border-b border-border">
                            <p className="text-[13px] font-bold lowercase text-text-primary font-mono">input</p>
                        </div>
                        <pre className="px-2.5 py-2 text-sm text-text-primary font-mono whitespace-pre-wrap">{tc.input}</pre>
                    </div>
                    <div className="border-t border-border">
                        <div className="px-2.5 py-1 bg-bg-surface border-b border-border">
                            <p className="text-[13px] font-bold lowercase text-text-primary font-mono">output</p>
                        </div>
                        <pre className="px-2.5 py-2 text-sm text-text-primary font-mono whitespace-pre-wrap">{tc.expected_output}</pre>
                    </div>
                </div>
            ))}
        </div>
    );

    return (
        <div className="h-[calc(100vh-64px)] bg-bg-root flex flex-col overflow-hidden">
            {/* Top Bar */}
            <div className="flex items-center justify-between px-4 py-3 bg-bg-primary border-b border-border shrink-0 shadow-[0_8px_16px_rgba(0,0,0,0.12)]">
                <div className="flex items-center gap-3">
                    <button
                        onClick={() => (isMockMode ? navigate('/mock-interview') : navigate(practiceBackPath))}
                        className="p-1.5 rounded-[12px_9px_11px_8px] hover:bg-bg-hover text-text-secondary hover:text-text-primary transition-colors"
                    >
                        <ArrowLeft size={18} />
                    </button>
                    <div>
                        <p className="editorial-kicker mb-1">Practice room</p>
                        <h2 className="text-sm font-bold text-text-primary truncate max-w-[200px] sm:max-w-[300px]">
                        {problem.title}
                        </h2>
                    </div>
                    <div
                        className={`h-6 w-6 rounded-md border flex items-center justify-center ${
                            problem.solved
                                ? 'border-[#6fbf73] bg-[#6fbf73]/15 text-[#6fbf73]'
                                : 'border-border bg-bg-surface text-transparent'
                        }`}
                        title={problem.solved ? 'Solved' : 'Not solved yet'}
                    >
                        <CheckCircle2 size={14} />
                    </div>
                    <Badge color={problem.difficulty === 'easy' ? 'green' : problem.difficulty === 'medium' ? 'yellow' : 'red'}>
                        {problem.difficulty}
                    </Badge>
                    {isMockMode && (
                        <span className="text-[10px] uppercase tracking-wider px-2 py-1 border border-accent/40 text-accent">
                            Mock interview
                        </span>
                    )}
                    {isCompetitiveProblem && (
                        <span className="px-2.5 py-1 rounded-full border border-[#7ec4cf]/30 bg-[#7ec4cf]/10 text-[#7ec4cf] text-xs font-semibold">
                            {problem.rating}
                        </span>
                    )}
                </div>
            </div>

            {/* Main Split */}
            <ResizableSplit
                defaultLeft={45}
                minLeft={25}
                maxLeft={65}
                left={
                    <div className="p-6 space-y-5">
                        {isCompetitiveProblem ? (
                            <>
                                <div>
                                    <h3 className="text-base font-bold text-text-primary mb-3">Problem statement</h3>
                                    <div className="text-sm text-text-secondary leading-7 whitespace-pre-wrap">
                                        {problem.description}
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-base font-bold text-text-primary mb-3">Input</h3>
                                    <div className="max-w-none">
                                        {renderCodeforcesTextBlock(problem.input_format)}
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-base font-bold text-text-primary mb-3">Output</h3>
                                    <div className="max-w-none">
                                        {renderCodeforcesTextBlock(problem.output_format)}
                                    </div>
                                </div>

                                {problem.constraints && (
                                    <div>
                                        <h3 className="text-base font-bold text-text-primary mb-3">Constraints</h3>
                                        <div className="text-sm text-text-secondary font-mono whitespace-pre-wrap leading-7">
                                            {problem.constraints}
                                        </div>
                                    </div>
                                )}

                                {problem.sample_cases?.length > 0 && (
                                    <div>
                                        <h3 className="text-base font-bold text-text-primary mb-3">Examples</h3>
                                        {formatCodeforcesExamples(problem.sample_cases)}
                                    </div>
                                )}
                            </>
                        ) : (
                            <>
                                <div>
                                    <h3 className="text-base font-bold text-text-primary mb-3">Problem statement</h3>
                                    <div className="text-sm text-text-secondary leading-7 whitespace-pre-wrap">
                                        {normalizeLeetCodeText(problem.description)}
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-base font-bold text-text-primary mb-3">Input</h3>
                                    <div className="text-sm text-text-secondary leading-7 whitespace-pre-wrap">
                                        {normalizeLeetCodeText(problem.input_format)}
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-base font-bold text-text-primary mb-3">Output</h3>
                                    <div className="text-sm text-text-secondary leading-7 whitespace-pre-wrap">
                                        {normalizeLeetCodeText(problem.output_format)}
                                    </div>
                                </div>

                                {problem.constraints && (
                                    <div>
                                        <h3 className="text-base font-bold text-text-primary mb-3">Constraints</h3>
                                        <div className="text-sm text-text-secondary font-mono whitespace-pre-wrap leading-7">
                                            {normalizeLeetCodeText(problem.constraints)}
                                        </div>
                                    </div>
                                )}

                                {problem.sample_cases?.length > 0 && (
                                    <div>
                                        <h3 className="text-base font-bold text-text-primary mb-3">Examples</h3>
                                        <div className="space-y-4">
                                            {problem.sample_cases.map((tc, i) => (
                                                <div key={i} className="border border-border bg-bg-primary overflow-hidden rounded-[6px]">
                                                    {problem.sample_cases.length > 1 && (
                                                        <div className="px-3 py-2 border-b border-border bg-bg-surface/60">
                                                            <p className="text-sm font-semibold text-text-primary">{`Example ${i + 1}`}</p>
                                                        </div>
                                                    )}
                                                    <div className="border-t border-border">
                                                        <div className="px-2.5 py-1 bg-bg-surface border-b border-border">
                                                            <p className="text-[13px] font-bold lowercase text-text-primary font-mono">input</p>
                                                        </div>
                                                        <pre className="px-2.5 py-2 text-sm text-text-primary font-mono whitespace-pre-wrap">{formatDsaSampleInput(tc)}</pre>
                                                    </div>
                                                    <div className="border-t border-border">
                                                        <div className="px-2.5 py-1 bg-bg-surface border-b border-border">
                                                            <p className="text-[13px] font-bold lowercase text-text-primary font-mono">output</p>
                                                        </div>
                                                        <pre className="px-2.5 py-2 text-sm text-text-primary font-mono whitespace-pre-wrap">{formatDsaSampleOutput(tc)}</pre>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </>
                        )}

                        {/* Submission History */}
                        {history.length > 0 && (
                            <div>
                                <h3 className="text-xs font-bold uppercase tracking-[0.18em] text-text-muted mb-3">
                                    Your Submissions ({history.length})
                                </h3>
                                <div className="space-y-1.5">
                                    {history.slice(0, 10).map((sub) => {
                                        const v = VERDICTS[sub.status];
                                        return (
                                            <div key={sub.id} className="flex items-center justify-between px-3 py-2 bg-bg-surface border border-border rounded-[12px_9px_11px_8px] text-xs">
                                                <span className="font-medium" style={{ color: v?.color }}>
                                                    {v?.icon} {v?.label || sub.status}
                                                </span>
                                                <span className="text-text-muted font-mono">
                                                    {sub.passed_test_cases}/{sub.total_test_cases}
                                                </span>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}
                    </div>
                }
                right={
                <div className="practice-editor-pane">
                    {/* Editor Toolbar */}
                    <div className="flex items-center justify-between px-4 py-2 bg-bg-primary border-b border-border shrink-0">
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2">
                                <Code2 className="w-4 h-4 text-text-secondary" />
                                <span className="text-xs font-semibold tracking-wide text-text-primary">editor</span>
                            </div>
                            <div className="relative group">
                                <select
                                    className="appearance-none bg-bg-surface border border-border hover:border-text-muted text-text-primary text-xs font-medium rounded-[12px_9px_11px_8px] px-3 py-1 pr-7 outline-none focus:border-accent transition-all cursor-pointer"
                                    value={language}
                                    onChange={(e) => handleLanguageChange(e.target.value)}
                                >
                                    {LANGUAGES.map((lang) => (
                                        <option key={lang.id} value={lang.id} className="bg-bg-primary text-text-primary">
                                            {lang.label}
                                        </option>
                                    ))}
                                </select>
                                <Settings2 className="w-3 h-3 text-text-muted absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={handleReset}
                                className="flex items-center gap-1.5 px-3 py-1 rounded-[12px_9px_11px_8px] text-xs font-medium text-text-secondary hover:text-text-primary hover:bg-bg-hover transition-colors"
                                title="Reset to template"
                            >
                                <RotateCcw className="w-3.5 h-3.5" />
                                Reset
                            </button>
                        </div>
                    </div>

                    {/* Monaco Editor */}
                    <div className="flex-1 w-full bg-bg-root relative min-h-0">
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
                                automaticLayout: true,
                                scrollbar: {
                                    verticalScrollbarSize: 10,
                                    horizontalScrollbarSize: 10,
                                },
                            }}
                        />
                    </div>

                    {/* Hint bar — DSA only, disabled during mock interview */}
                    {!isCompetitiveProblem && !isMockMode && (
                        <div className="shrink-0 border-t border-border bg-bg-surface/50 px-4 py-2 flex flex-wrap items-center gap-2">
                            <span className="text-[10px] uppercase tracking-wider text-text-muted mr-1">AI hints</span>
                            {['nudge', 'pattern', 'outline'].map((level) => (
                                <button
                                    key={level}
                                    type="button"
                                    disabled={hintLoading}
                                    onClick={() => handleHint(level)}
                                    className="px-2.5 py-1 text-xs border border-border hover:border-accent/40 capitalize disabled:opacity-50"
                                >
                                    {level}
                                </button>
                            ))}
                            {hintText && (
                                <p className="w-full text-xs text-text-secondary mt-1 border-l-2 border-accent pl-2">{hintText}</p>
                            )}
                        </div>
                    )}

                    {/* Bottom Action Bar (LeetCode-style) */}
                    <div className="shrink-0 border-t border-border bg-bg-primary px-4 py-3">
                        <div className="flex items-center justify-end gap-2">
                            <button
                                onClick={handleRun}
                                disabled={runMutation.isPending || submitMutation.isPending || polling || !code.trim()}
                                className={`flex items-center gap-1.5 px-4 py-1.5 rounded-[12px_9px_11px_8px] text-xs font-bold transition-all ${
                                    !runMutation.isPending && !submitMutation.isPending && !polling && code.trim()
                                        ? 'bg-bg-surface hover:bg-bg-hover text-text-primary border border-border-hover'
                                        : 'bg-bg-surface border border-border text-text-muted cursor-not-allowed'
                                }`}
                            >
                                {runMutation.isPending ? (
                                    <>
                                        <span className="w-3.5 h-3.5 border-2 border-text-muted/30 border-t-text-primary rounded-full animate-spin"></span>
                                        Running Samples
                                    </>
                                ) : (
                                    <>
                                        <Play className="w-3.5 h-3.5" />
                                        Run
                                    </>
                                )}
                            </button>

                            <button
                                onClick={handleSubmit}
                                disabled={submitMutation.isPending || polling || runMutation.isPending || !code.trim()}
                                className={`flex items-center gap-1.5 px-4 py-1.5 rounded-[12px_9px_11px_8px] text-xs font-bold transition-all ${
                                    !submitMutation.isPending && !polling && !runMutation.isPending && code.trim()
                                        ? 'bg-accent hover:bg-accent-hover text-white border border-[#e29a6c] shadow-[3px_3px_0_rgba(0,0,0,0.16)]'
                                        : 'bg-bg-surface border border-border text-text-muted cursor-not-allowed'
                                }`}
                            >
                                {submitMutation.isPending || polling ? (
                                    <>
                                        <span className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
                                        Submitting
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

                    {/* Run Result Panel (samples only) */}
                    {runResult && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="shrink-0 border-t border-border bg-bg-primary px-4 py-3"
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <span
                                        className="text-sm font-bold"
                                        style={{ color: VERDICTS[runResult.status]?.color || 'var(--text-primary)' }}
                                    >
                                        Run: {VERDICTS[runResult.status]?.label || runResult.status}
                                    </span>
                                    {runResult.message && (
                                        <span className="text-xs text-loss">{runResult.message}</span>
                                    )}
                                </div>
                                <div className="flex items-center gap-4 text-xs text-text-secondary">
                                    <span className="font-mono">
                                        {runResult.passed_test_cases ?? 0}/{runResult.total_test_cases ?? 0} sample cases passed
                                    </span>
                                    {runResult.execution_time_ms != null && (
                                        <span className="font-mono">{runResult.execution_time_ms}ms</span>
                                    )}
                                    {runResult.memory_used_kb != null && (
                                        <span className="font-mono">{(runResult.memory_used_kb / 1024).toFixed(1)}MB</span>
                                    )}
                                </div>
                            </div>

                            {runResult.cases?.length > 0 && (
                                <div className="mt-3 space-y-2 max-h-56 overflow-auto pr-1">
                                    {runResult.cases.map((tc, idx) => (
                                        <div key={`${tc.order_index}-${idx}`} className="bg-bg-root rounded-[12px_9px_11px_8px] p-3 border border-border">
                                            <div className="flex items-center justify-between mb-2">
                                                <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-text-muted">Sample #{idx + 1}</p>
                                                <span className="text-xs font-semibold" style={{ color: VERDICTS[tc.verdict]?.color || 'var(--text-primary)' }}>
                                                    {VERDICTS[tc.verdict]?.label || tc.verdict}
                                                </span>
                                            </div>
                                            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                                                <div>
                                                    <p className="text-[10px] font-bold uppercase text-text-muted mb-1">Input</p>
                                                    <pre className="text-xs text-text-primary font-mono whitespace-pre-wrap">{tc.input}</pre>
                                                </div>
                                                <div>
                                                    <p className="text-[10px] font-bold uppercase text-text-muted mb-1">Expected</p>
                                                    <pre className="text-xs text-text-primary font-mono whitespace-pre-wrap">{tc.expected_output}</pre>
                                                </div>
                                                <div>
                                                    <p className="text-[10px] font-bold uppercase text-text-muted mb-1">Actual</p>
                                                    <pre className="text-xs font-mono whitespace-pre-wrap text-text-primary">{tc.error_output || tc.actual_output || 'No output'}</pre>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </motion.div>
                    )}

                    {/* Verdict Panel */}
                    {verdict && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="shrink-0 border-t border-border bg-bg-primary px-4 py-3"
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    {StatusIcon && (
                                        <StatusIcon
                                            size={20}
                                            style={{ color: verdictInfo?.color }}
                                        />
                                    )}
                                    {polling && (
                                        <span className="w-5 h-5 border-2 border-accent/30 border-t-accent rounded-full animate-spin" />
                                    )}
                                    <span
                                        className="text-sm font-bold"
                                        style={{ color: verdictInfo?.color || 'var(--text-primary)' }}
                                    >
                                        {verdictInfo?.label || verdict.status || 'Running...'}
                                    </span>
                                    {/* AI Loading indicator */}
                                    {!isCompetitiveProblem && aiLoading && !polling && (
                                        <div className="flex items-center gap-1.5 text-accent text-xs font-medium">
                                            <Sparkles size={13} className="animate-pulse" />
                                            Analyzing with AI...
                                        </div>
                                    )}
                                </div>
                                <div className="flex items-center gap-4 text-xs text-text-secondary">
                                    <span className="font-mono">
                                        {verdict.passed_test_cases ?? '?'}/{verdict.total_test_cases ?? '?'} passed
                                    </span>
                                    {verdict.execution_time_ms != null && (
                                        <span className="font-mono">{verdict.execution_time_ms}ms</span>
                                    )}
                                    {verdict.memory_used_kb != null && (
                                        <span className="font-mono">{(verdict.memory_used_kb / 1024).toFixed(1)}MB</span>
                                    )}
                                    {/* Re-open AI panel button */}
                                    {!isCompetitiveProblem && !isMockMode && aiAnalysis && !showAIPanel && (
                                        <button
                                            onClick={() => setShowAIPanel(true)}
                                            className="flex items-center gap-1 px-2.5 py-1 rounded-[12px_9px_11px_8px] bg-accent/10 text-accent border border-accent/20 hover:bg-accent/20 transition-colors text-xs font-semibold"
                                        >
                                            <Sparkles size={11} />
                                            View AI Analysis
                                        </button>
                                    )}
                                </div>
                            </div>
                            {verdict.status === 'error' && verdict.message && (
                                <p className="text-xs text-loss mt-2">{verdict.message}</p>
                            )}

                            {verdict.status !== 'accepted' && verdict.status !== 'running' && verdict.status !== 'queued' && verdict.failed_test_case && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    className="mt-4 pt-4 border-t border-border"
                                >
                                    <h3 className="text-xs font-bold uppercase tracking-[0.18em] text-text-muted mb-3 flex items-center gap-2">
                                        <AlertTriangle size={14} className="text-loss" />
                                        Failed Test Case
                                    </h3>
                                    
                                    <div className="space-y-3">
                                        <div className="bg-bg-root rounded-[12px_9px_11px_8px] p-3 border border-border">
                                            <p className="text-[10px] font-bold uppercase text-text-muted mb-1">Input</p>
                                            <pre className="text-xs text-text-primary font-mono whitespace-pre-wrap">{verdict.failed_test_case.input}</pre>
                                        </div>
                                        
                                        <div className="grid grid-cols-2 gap-3">
                                            <div className="bg-bg-root rounded-[12px_9px_11px_8px] p-3 border border-border">
                                                <p className="text-[10px] font-bold uppercase text-text-muted mb-1">Expected Output</p>
                                                <pre className="text-xs text-text-primary font-mono whitespace-pre-wrap">{verdict.failed_test_case.expected_output}</pre>
                                            </div>
                                            
                                            <div className="bg-bg-root rounded-[12px_9px_11px_8px] p-3 border border-loss/30">
                                                <p className="text-[10px] font-bold uppercase text-loss mb-1">Actual Output / Error</p>
                                                <pre className="text-xs font-mono whitespace-pre-wrap text-loss/90">
                                                    {verdict.failed_test_case.error_output || verdict.failed_test_case.actual_output || "No output generated"}
                                                </pre>
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </motion.div>
                    )}
                </div>
                }
            />

            {/* AI Analysis Modal - auto-pops after every verdict */}
            <AnimatePresence>
                {!isCompetitiveProblem && !isMockMode && showAIPanel && (
                    aiLoading ? (
                        <motion.div
                            key="ai-loading"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="fixed inset-0 z-50 flex items-center justify-center"
                            style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(6px)' }}
                        >
                            <div className="flex flex-col items-center gap-5 text-center">
                                <div className="w-16 h-16 rounded-2xl bg-accent/20 flex items-center justify-center">
                                    <Sparkles size={28} className="text-accent animate-pulse" />
                                </div>
                                <div>
                                    <p className="text-text-primary font-bold text-base mb-1">Analyzing your code...</p>
                                    <p className="text-text-muted text-sm">AI is preparing a clearer explanation for your submission</p>
                                </div>
                                <div className="flex gap-1.5">
                                    {[0, 1, 2].map((i) => (
                                        <motion.span
                                            key={i}
                                            className="w-2 h-2 rounded-full bg-accent"
                                            animate={{ opacity: [0.3, 1, 0.3] }}
                                            transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
                                        />
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    ) : (
                        <AIAnalysisPanel
                            key="ai-panel"
                            analysis={aiAnalysis}
                            verdict={verdict}
                            onClose={() => setShowAIPanel(false)}
                            shareSlug={shareSlug}
                            onShare={shareSlug ? handleShareInsight : undefined}
                        />
                    )
                )}
            </AnimatePresence>
        </div>
    );
}
