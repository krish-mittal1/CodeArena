/**
 * Custom Monaco editor theme — "CodeArena Warm"
 *
 * Designed to blend seamlessly with the app's warm dark palette
 * instead of the jarring blue-gray default vs-dark.
 */

export const CODEARENA_THEME_NAME = 'codearena-warm';

export function defineCodeArenaTheme(monaco) {
    monaco.editor.defineTheme(CODEARENA_THEME_NAME, {
        base: 'vs-dark',
        inherit: true,
        rules: [
            // ── Comments ────────────────────────────────
            { token: 'comment',          foreground: '6d5e4e', fontStyle: 'italic' },
            { token: 'comment.doc',      foreground: '7a6b5a', fontStyle: 'italic' },

            // ── Keywords & Control Flow ─────────────────
            { token: 'keyword',          foreground: 'e09f68' },
            { token: 'keyword.control',  foreground: 'e09f68' },
            { token: 'keyword.operator', foreground: 'c6b49b' },

            // ── Strings ─────────────────────────────────
            { token: 'string',           foreground: 'a3c47a' },
            { token: 'string.escape',    foreground: 'd4b896' },

            // ── Numbers ─────────────────────────────────
            { token: 'number',           foreground: 'd4976a' },
            { token: 'number.float',     foreground: 'd4976a' },
            { token: 'number.hex',       foreground: 'd4976a' },

            // ── Types & Classes ─────────────────────────
            { token: 'type',             foreground: '7ec4cf' },
            { token: 'type.identifier',  foreground: '7ec4cf' },
            { token: 'class',            foreground: '7ec4cf' },

            // ── Functions ───────────────────────────────
            { token: 'function',         foreground: 'dcc080' },
            { token: 'function.declaration', foreground: 'dcc080' },

            // ── Variables & Identifiers ─────────────────
            { token: 'variable',         foreground: 'f1e6d4' },
            { token: 'variable.predefined', foreground: 'c9a87a' },
            { token: 'identifier',       foreground: 'f1e6d4' },

            // ── Operators & Punctuation ─────────────────
            { token: 'operator',         foreground: 'c6b49b' },
            { token: 'delimiter',        foreground: '8d7965' },
            { token: 'delimiter.bracket',foreground: 'a89480' },
            { token: 'delimiter.parenthesis', foreground: 'a89480' },

            // ── Constants ───────────────────────────────
            { token: 'constant',         foreground: 'd4976a' },

            // ── Tags (JSX/HTML) ─────────────────────────
            { token: 'tag',              foreground: 'e09f68' },
            { token: 'attribute.name',   foreground: 'dcc080' },
            { token: 'attribute.value',  foreground: 'a3c47a' },

            // ── Regex ───────────────────────────────────
            { token: 'regexp',           foreground: 'd4976a' },
        ],
        colors: {
            // ── Editor background & foreground ──────────
            'editor.background':                '#1a1613',
            'editor.foreground':                '#f1e6d4',

            // ── Line highlight ──────────────────────────
            'editor.lineHighlightBackground':   '#251f1a',
            'editor.lineHighlightBorder':       '#00000000',

            // ── Selection ───────────────────────────────
            'editor.selectionBackground':       '#c96d3a30',
            'editor.inactiveSelectionBackground':'#c96d3a18',
            'editor.selectionHighlightBackground':'#c96d3a15',

            // ── Find match highlights ───────────────────
            'editor.findMatchBackground':       '#c96d3a40',
            'editor.findMatchHighlightBackground':'#c96d3a20',

            // ── Cursor ──────────────────────────────────
            'editorCursor.foreground':          '#e0a06a',

            // ── Line numbers ────────────────────────────
            'editorLineNumber.foreground':      '#5a4a3d',
            'editorLineNumber.activeForeground':'#a89480',

            // ── Indentation guides ──────────────────────
            'editorIndentGuide.background':     '#2e2620',
            'editorIndentGuide.activeBackground':'#4b3f34',

            // ── Gutter ──────────────────────────────────
            'editorGutter.background':          '#1a1613',

            // ── Scrollbar ───────────────────────────────
            'scrollbar.shadow':                 '#00000000',
            'scrollbarSlider.background':       '#5a4a3d60',
            'scrollbarSlider.hoverBackground':  '#6c5a4b80',
            'scrollbarSlider.activeBackground': '#8d7965a0',

            // ── Widget (autocomplete, hover tooltips) ───
            'editorWidget.background':          '#211c18',
            'editorWidget.border':              '#4b3f34',
            'editorSuggestWidget.background':   '#211c18',
            'editorSuggestWidget.border':       '#4b3f34',
            'editorSuggestWidget.selectedBackground': '#342c25',
            'editorSuggestWidget.highlightForeground': '#e0a06a',

            // ── Hover widget ────────────────────────────
            'editorHoverWidget.background':     '#211c18',
            'editorHoverWidget.border':         '#4b3f34',

            // ── Bracket match ───────────────────────────
            'editorBracketMatch.background':    '#c96d3a20',
            'editorBracketMatch.border':        '#c96d3a60',

            // ── Minimap (if ever enabled) ───────────────
            'minimap.background':               '#1a1613',

            // ── Overview ruler ───────────────────────────
            'editorOverviewRuler.border':       '#00000000',
        },
    });
}
