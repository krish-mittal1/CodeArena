import Editor from '@monaco-editor/react';
import { useBattleStore } from '../../stores/battleStore';
import { submissionApi } from '../../api/auth';
import { LANGUAGES, CODE_TEMPLATES } from '../../utils/constants';
import { Code2, Play, RotateCcw, Settings2 } from 'lucide-react';

export default function CodeEditor() {
    const language = useBattleStore((s) => s.language);
    const code = useBattleStore((s) => s.code);
    const matchId = useBattleStore((s) => s.matchId);
    const problem = useBattleStore((s) => s.problem);
    const submissionStatus = useBattleStore((s) => s.submissionStatus);
    const matchResult = useBattleStore((s) => s.matchResult);

    const setLanguage = useBattleStore((s) => s.setLanguage);
    const setCode = useBattleStore((s) => s.setCode);
    const setSubmissionStatus = useBattleStore((s) => s.setSubmissionStatus);

    const monacoLang = LANGUAGES.find((l) => l.id === language)?.monacoId || 'python';

    // Derived states
    const isSubmitting = submissionStatus === 'submitting' || submissionStatus === 'running';
    const canSubmit = !isSubmitting && !matchResult && code.trim().length > 0;

    const handleSubmit = async () => {
        if (!canSubmit || !matchId || !problem) return;

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
            setSubmissionStatus('idle');
        }
    };

    const handleReset = () => {
        setCode(CODE_TEMPLATES[language] || '');
    };

    return (
        <div className="flex flex-col flex-1 h-full bg-bg-root overflow-hidden relative">
            {/* Sleek Toolbar Header */}
            <div className="flex items-center justify-between px-4 py-2 bg-bg-primary border-b border-border shrink-0 z-10">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <Code2 className="w-4 h-4 text-text-secondary" />
                        <span className="text-xs font-semibold tracking-wide text-text-primary">editor</span>
                    </div>

                    {/* Modern subtle language dropdown */}
                    <div className="relative group">
                        <select
                            className="appearance-none bg-bg-surface border border-border hover:border-text-muted text-text-primary text-xs font-medium rounded-sm px-3 py-1 pr-7 outline-none focus:border-accent transition-all cursor-pointer"
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

                {/* Primary Action Buttons */}
                <div className="flex items-center gap-2">
                    <button
                        onClick={handleReset}
                        disabled={!!matchResult}
                        className="flex items-center gap-1.5 px-3 py-1 rounded-sm text-xs font-medium text-text-secondary hover:text-text-primary hover:bg-bg-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Reset to template"
                    >
                        <RotateCcw className="w-3.5 h-3.5" />
                        Reset
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={!canSubmit}
                        className={`flex items-center gap-1.5 px-4 py-1 rounded-sm text-xs font-bold transition-all ${canSubmit
                            ? 'bg-win hover:bg-win/90 text-white'
                            : 'bg-bg-surface border border-border text-text-muted cursor-not-allowed'
                            }`}
                    >
                        {isSubmitting ? (
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

            {/* Monaco Editor Container */}
            <div className="flex-1 w-full bg-bg-root relative">
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
