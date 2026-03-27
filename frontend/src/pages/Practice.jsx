import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Editor from '@monaco-editor/react';
import {
    ArrowLeft, Code2, Play, RotateCcw, Settings2,
    CheckCircle2, XCircle, Clock, AlertTriangle,
} from 'lucide-react';
import { problemApi, practiceApi } from '../api/auth';
import { LANGUAGES, CODE_TEMPLATES, VERDICTS } from '../utils/constants';
import Badge from '../components/ui/Badge';

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
    const [language, setLanguage] = useState('python');
    const [code, setCode] = useState(CODE_TEMPLATES['python'] || '');
    const [verdict, setVerdict] = useState(null);
    const [polling, setPolling] = useState(false);
    const [submissionId, setSubmissionId] = useState(null);

    const { data: problem, isLoading } = useQuery({
        queryKey: ['problem', problemId],
        queryFn: () => problemApi.getById(problemId),
        enabled: !!problemId,
    });

    const { data: history = [], refetch: refetchHistory } = useQuery({
        queryKey: ['practiceHistory', problemId],
        queryFn: () => practiceApi.getSubmissions(problemId),
        enabled: !!problemId,
    });

    const monacoLang = LANGUAGES.find((l) => l.id === language)?.monacoId || 'python';

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
                } else if (sub) {
                    setVerdict(sub);
                }
            } catch {
                // ignore polling errors
            }
        }, 1500);

        return () => clearInterval(interval);
    }, [polling, submissionId, problemId, refetchHistory]);

    const handleSubmit = () => {
        if (submitMutation.isPending || !code.trim()) return;
        setVerdict(null);
        submitMutation.mutate({
            problem_id: problemId,
            language,
            code,
        });
    };

    const handleReset = () => {
        setCode(CODE_TEMPLATES[language] || '');
        setVerdict(null);
    };

    const handleLanguageChange = (newLang) => {
        setLanguage(newLang);
        setCode(CODE_TEMPLATES[newLang] || '');
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-bg-root flex items-center justify-center">
                <div className="text-center">
                    <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center mx-auto mb-3 animate-pulse">
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

    return (
        <div className="h-[calc(100vh-64px)] bg-bg-root flex flex-col overflow-hidden">
            {/* Top Bar */}
            <div className="flex items-center justify-between px-4 py-2 bg-bg-primary border-b border-border shrink-0">
                <div className="flex items-center gap-3">
                    <button
                        onClick={() => navigate('/problems')}
                        className="p-1.5 rounded-md hover:bg-bg-hover text-text-secondary hover:text-text-primary transition-colors"
                    >
                        <ArrowLeft size={18} />
                    </button>
                    <h2 className="text-sm font-bold text-text-primary truncate max-w-[300px]">
                        {problem.title}
                    </h2>
                    <Badge color={problem.difficulty === 'easy' ? 'green' : problem.difficulty === 'medium' ? 'yellow' : 'red'}>
                        {problem.difficulty}
                    </Badge>
                </div>
            </div>

            {/* Main Split */}
            <div className="flex-1 flex overflow-hidden">
                {/* Left: Problem Description */}
                <div className="w-[45%] min-w-[350px] border-r border-border overflow-y-auto">
                    <div className="p-6 space-y-5">
                        {/* Description */}
                        <div>
                            <h3 className="text-xs font-bold uppercase tracking-wider text-text-muted mb-3">Description</h3>
                            <div className="text-sm text-text-secondary leading-relaxed whitespace-pre-wrap">
                                {problem.description}
                            </div>
                        </div>

                        {/* Input Format */}
                        <div>
                            <h3 className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2">Input Format</h3>
                            <p className="text-sm text-text-secondary">{problem.input_format}</p>
                        </div>

                        {/* Output Format */}
                        <div>
                            <h3 className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2">Output Format</h3>
                            <p className="text-sm text-text-secondary">{problem.output_format}</p>
                        </div>

                        {/* Constraints */}
                        {problem.constraints && (
                            <div>
                                <h3 className="text-xs font-bold uppercase tracking-wider text-text-muted mb-2">Constraints</h3>
                                <p className="text-sm text-text-secondary font-mono">{problem.constraints}</p>
                            </div>
                        )}

                        {/* Sample Cases */}
                        {problem.sample_cases?.length > 0 && (
                            <div>
                                <h3 className="text-xs font-bold uppercase tracking-wider text-text-muted mb-3">Examples</h3>
                                <div className="space-y-3">
                                    {problem.sample_cases.map((tc, i) => (
                                        <div key={i} className="bg-bg-surface border border-border rounded-lg overflow-hidden">
                                            <div className="grid grid-cols-2 divide-x divide-border">
                                                <div className="p-3">
                                                    <p className="text-[10px] font-bold uppercase text-text-muted mb-1">Input</p>
                                                    <pre className="text-xs text-text-primary font-mono whitespace-pre-wrap">{tc.input}</pre>
                                                </div>
                                                <div className="p-3">
                                                    <p className="text-[10px] font-bold uppercase text-text-muted mb-1">Output</p>
                                                    <pre className="text-xs text-text-primary font-mono whitespace-pre-wrap">{tc.expected_output}</pre>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Submission History */}
                        {history.length > 0 && (
                            <div>
                                <h3 className="text-xs font-bold uppercase tracking-wider text-text-muted mb-3">
                                    Your Submissions ({history.length})
                                </h3>
                                <div className="space-y-1.5">
                                    {history.slice(0, 10).map((sub) => {
                                        const v = VERDICTS[sub.status];
                                        return (
                                            <div key={sub.id} className="flex items-center justify-between px-3 py-2 bg-bg-surface border border-border rounded-md text-xs">
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
                </div>

                {/* Right: Editor + Verdict */}
                <div className="flex-1 flex flex-col overflow-hidden">
                    {/* Editor Toolbar */}
                    <div className="flex items-center justify-between px-4 py-2 bg-bg-primary border-b border-border shrink-0">
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2">
                                <Code2 className="w-4 h-4 text-text-secondary" />
                                <span className="text-xs font-semibold tracking-wide text-text-primary">editor</span>
                            </div>
                            <div className="relative group">
                                <select
                                    className="appearance-none bg-bg-surface border border-border hover:border-text-muted text-text-primary text-xs font-medium rounded-sm px-3 py-1 pr-7 outline-none focus:border-accent transition-all cursor-pointer"
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
                                className="flex items-center gap-1.5 px-3 py-1 rounded-sm text-xs font-medium text-text-secondary hover:text-text-primary hover:bg-bg-hover transition-colors"
                                title="Reset to template"
                            >
                                <RotateCcw className="w-3.5 h-3.5" />
                                Reset
                            </button>
                            <button
                                onClick={handleSubmit}
                                disabled={submitMutation.isPending || polling || !code.trim()}
                                className={`flex items-center gap-1.5 px-4 py-1 rounded-sm text-xs font-bold transition-all ${
                                    !submitMutation.isPending && !polling && code.trim()
                                        ? 'bg-win hover:bg-win/90 text-white'
                                        : 'bg-bg-surface border border-border text-text-muted cursor-not-allowed'
                                }`}
                            >
                                {submitMutation.isPending || polling ? (
                                    <>
                                        <span className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
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

                    {/* Monaco Editor */}
                    <div className="flex-1 w-full bg-bg-root relative min-h-0">
                        <Editor
                            height="100%"
                            language={monacoLang}
                            value={code}
                            onChange={(value) => setCode(value || '')}
                            theme="vs-dark"
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
                                    <h3 className="text-xs font-bold uppercase tracking-wider text-text-muted mb-3 flex items-center gap-2">
                                        <AlertTriangle size={14} className="text-loss" />
                                        Failed Test Case
                                    </h3>
                                    
                                    <div className="space-y-3">
                                        <div className="bg-bg-root rounded-md p-3 border border-border">
                                            <p className="text-[10px] font-bold uppercase text-text-muted mb-1">Input</p>
                                            <pre className="text-xs text-text-primary font-mono whitespace-pre-wrap">{verdict.failed_test_case.input}</pre>
                                        </div>
                                        
                                        <div className="grid grid-cols-2 gap-3">
                                            <div className="bg-bg-root rounded-md p-3 border border-border">
                                                <p className="text-[10px] font-bold uppercase text-text-muted mb-1">Expected Output</p>
                                                <pre className="text-xs text-text-primary font-mono whitespace-pre-wrap">{verdict.failed_test_case.expected_output}</pre>
                                            </div>
                                            
                                            <div className="bg-bg-root rounded-md p-3 border border-loss/30">
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
            </div>
        </div>
    );
}
