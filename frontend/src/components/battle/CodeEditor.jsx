import Editor from '@monaco-editor/react';
import { useBattleStore } from '../../stores/battleStore';
import { submissionApi } from '../../api/auth';
import { LANGUAGES, CODE_TEMPLATES } from '../../utils/constants';
import styles from './CodeEditor.module.css';

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
    const canSubmit =
        submissionStatus !== 'submitting' &&
        submissionStatus !== 'running' &&
        !matchResult &&
        code.trim().length > 0;

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
            // Immediately transition to "running" after API success.
            // The WS submission_result event will later set it to "judged".
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
        <div className={styles.editorPanel}>
            {/* Toolbar */}
            <div className={styles.toolbar}>
                <div className={styles.toolbarLeft}>
                    <span className={styles.toolbarTitle}>💻 Editor</span>
                    <select
                        className={styles.langSelect}
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        disabled={!!matchResult}
                    >
                        {LANGUAGES.map((lang) => (
                            <option key={lang.id} value={lang.id}>
                                {lang.label}
                            </option>
                        ))}
                    </select>
                </div>

                <div className={styles.toolbarRight}>
                    <button
                        className={styles.resetBtn}
                        onClick={handleReset}
                        disabled={!!matchResult}
                        title="Reset to template"
                    >
                        ↺ Reset
                    </button>
                    <button
                        className={styles.submitBtn}
                        onClick={handleSubmit}
                        disabled={!canSubmit}
                    >
                        {submissionStatus === 'submitting' || submissionStatus === 'running'
                            ? '⏳ Running...'
                            : '▶ Submit'}
                    </button>
                </div>
            </div>

            {/* Monaco Editor */}
            <div className={styles.editorWrap}>
                <Editor
                    height="100%"
                    language={monacoLang}
                    value={code}
                    onChange={(value) => setCode(value || '')}
                    theme="vs-dark"
                    options={{
                        fontSize: 14,
                        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                        minimap: { enabled: false },
                        scrollBeyondLastLine: false,
                        padding: { top: 12 },
                        lineNumbers: 'on',
                        renderLineHighlight: 'line',
                        cursorBlinking: 'smooth',
                        smoothScrolling: true,
                        wordWrap: 'on',
                        tabSize: 4,
                        readOnly: !!matchResult,
                        automaticLayout: true,
                    }}
                />
            </div>
        </div>
    );
}
