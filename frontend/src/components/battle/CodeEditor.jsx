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
        <div className="flex flex-col flex-1 h-full bg-slate-950 overflow-hidden relative">
            {/* Sleek Toolbar Header */}
            <div className="flex items-center justify-between px-6 py-3 bg-slate-900 border-b border-slate-800 shrink-0 z-10">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 text-white">
                        <Code2 className="w-5 h-5 text-indigo-400" />
                        <span className="text-sm font-semibold tracking-wide">Workspace</span>
                    </div>

                    {/* Modern subtle language dropdown */}
                    <div className="relative group">
                        <select
                            className="appearance-none bg-slate-950 border border-slate-800 hover:border-slate-700 text-slate-300 text-sm font-medium rounded-lg px-4 py-1.5 pr-8 outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all cursor-pointer"
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                            disabled={!!matchResult}
                        >
                            {LANGUAGES.map((lang) => (
                                <option key={lang.id} value={lang.id} className="bg-slate-900 text-slate-300">
                                    {lang.label}
                                </option>
                            ))}
                        </select>
                        <Settings2 className="w-4 h-4 text-slate-500 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none group-hover:text-slate-400 transition-colors" />
                    </div>
                </div>

                {/* Primary Action Buttons Pinned Top Right */}
                <div className="flex items-center gap-3">
                    <button
                        onClick={handleReset}
                        disabled={!!matchResult}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        title="Reset to template"
                    >
                        <RotateCcw className="w-4 h-4" />
                        Reset
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={!canSubmit}
                        className={`flex items-center gap-2 px-5 py-1.5 rounded-lg text-sm font-bold shadow-sm transition-all ${canSubmit
                            ? 'bg-indigo-600 hover:bg-indigo-500 text-white'
                            : 'bg-slate-800 text-slate-500 cursor-not-allowed shadow-none'
                            }`}
                    >
                        {isSubmitting ? (
                            <>
                                <span className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></span>
                                Running...
                            </>
                        ) : (
                            <>
                                <Play className="w-4 h-4 fill-current" />
                                Submit
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Monaco Editor Container */}
            <div className="flex-1 w-full bg-slate-950 relative">
                <Editor
                    height="100%"
                    language={monacoLang}
                    value={code}
                    onChange={(value) => setCode(value || '')}
                    theme="vs-dark"
                    options={{
                        fontSize: 14,
                        fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
                        minimap: { enabled: false },
                        scrollBeyondLastLine: false,
                        padding: { top: 16, bottom: 16 },
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
