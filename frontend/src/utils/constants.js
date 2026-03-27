/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Frontend Constants — mirrors backend's core/constants.py
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

// Your Azure VM Public IP: 4.193.212.14
const PROD_IP = '4.193.212.14';

export const API_BASE = import.meta.env.VITE_API_URL || `http://${PROD_IP}:8000/api/v1`;
export const WS_BASE = import.meta.env.VITE_WS_URL || `ws://${PROD_IP}:8000`;

// ── WebSocket Events (mirrors WSEvent enum) ──────────
export const WS_EVENTS = {
    // Server → Client
    CONNECTED: 'connected',
    MATCH_FOUND: 'match_found',
    ROOM_JOINED: 'room_joined',
    MATCH_TIMER_SYNC: 'match_timer_sync',
    SUBMISSION_QUEUED: 'submission_queued',
    SUBMISSION_RUNNING: 'submission_running',
    SUBMISSION_RESULT: 'submission_result',
    OPPONENT_SUBMITTED: 'opponent_submitted',
    MATCH_ENDED: 'match_ended',
    PLAYER_DISCONNECTED: 'player_disconnected',
    SPECTATOR_UPDATE: 'spectator_update',
    SPECTATOR_JOINED: 'spectator_joined',
    ERROR: 'error',

    // Client → Server
    HEARTBEAT: 'heartbeat',
};

// ── Verdict labels + colors ─────────────────────────
export const VERDICTS = {
    accepted: { label: 'Accepted', color: 'var(--color-accepted)', icon: '✓' },
    wrong_answer: { label: 'Wrong Answer', color: 'var(--color-wrong)', icon: '✗' },
    tle: { label: 'Time Limit Exceeded', color: 'var(--color-tle)', icon: '⏱' },
    mle: { label: 'Memory Limit Exceeded', color: 'var(--color-mle)', icon: '💾' },
    runtime_error: { label: 'Runtime Error', color: 'var(--color-rte)', icon: '💥' },
    compilation_error: { label: 'Compilation Error', color: 'var(--color-rte)', icon: '⚙' },
    queued: { label: 'Queued', color: 'var(--color-queued)', icon: '⏳' },
    running: { label: 'Running', color: 'var(--accent-primary)', icon: '▶' },
};

// ── Languages supported ─────────────────────────────
export const LANGUAGES = [
    { id: 'python', label: 'Python 3', monacoId: 'python' },
    { id: 'cpp', label: 'C++ 17', monacoId: 'cpp' },
    { id: 'java', label: 'Java 21', monacoId: 'java' },
    { id: 'javascript', label: 'JavaScript', monacoId: 'javascript' },
];

// ── Default code templates (Standard I/O fallback) ────────
export const CODE_TEMPLATES = {
    python: 'import sys\n\ndef solve():\n    # Read from sys.stdin\n    # input_data = sys.stdin.read().split()\n    pass\n\nif __name__ == "__main__":\n    solve()\n',
    cpp: '#include <iostream>\n#include <string>\n#include <vector>\n#include <algorithm>\n\nusing namespace std;\n\nint main() {\n    // Optimize standard I/O operations for performance\n    ios_base::sync_with_stdio(false);\n    cin.tie(NULL);\n    \n    // Write your solution here\n    \n    return 0;\n}\n',
    java: 'import java.util.*;\nimport java.io.*;\n\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner scanner = new Scanner(System.in);\n        // Write your solution here\n        \n    }\n}\n',
    javascript: 'const fs = require("fs");\n\nfunction solve() {\n    const input = fs.readFileSync("/dev/stdin", "utf-8").trim().split("\\n");\n    // Write your solution here\n    \n}\n\nsolve();\n',
};

// ── Type mappings for boilerplate generation ────────
const TYPE_MAPS = {
    python: {
        'int': 'int', 'int[]': 'List[int]', 'int[][]': 'List[List[int]]',
        'str': 'str', 'str[]': 'List[str]', 'bool': 'bool',
        'float': 'float', 'float[]': 'List[float]',
    },
    cpp: {
        'int': 'int', 'int[]': 'vector<int>', 'int[][]': 'vector<vector<int>>',
        'str': 'string', 'str[]': 'vector<string>', 'bool': 'bool',
        'float': 'double', 'float[]': 'vector<double>',
    },
    java: {
        'int': 'int', 'int[]': 'int[]', 'int[][]': 'int[][]',
        'str': 'String', 'str[]': 'String[]', 'bool': 'boolean',
        'float': 'double', 'float[]': 'double[]',
    },
    javascript: {
        'int': 'number', 'int[]': 'number[]', 'int[][]': 'number[][]',
        'str': 'string', 'str[]': 'string[]', 'bool': 'boolean',
        'float': 'number', 'float[]': 'number[]',
    },
};

/**
 * Generate problem-specific class Solution boilerplate from API signature.
 * Falls back to generic CODE_TEMPLATES if no signature is available.
 */
export function generateBoilerplate(language, problem) {
    if (!problem?.method_name || !problem?.parameters || !problem?.return_type) {
        return CODE_TEMPLATES[language] || '';
    }

    const { method_name, parameters, return_type } = problem;
    const map = TYPE_MAPS[language] || TYPE_MAPS.python;

    if (language === 'python') {
        const params = parameters.map(p => `${p.name}: ${map[p.type] || 'Any'}`).join(', ');
        const retType = map[return_type] || 'Any';
        return `from typing import List, Optional\n\nclass Solution:\n    def ${method_name}(self, ${params}) -> ${retType}:\n        # Write your solution here\n        pass\n`;
    }

    if (language === 'cpp') {
        const params = parameters.map(p => `${map[p.type] || 'int'}& ${p.name}`).join(', ');
        const retType = map[return_type] || 'int';
        return `#include <bits/stdc++.h>\nusing namespace std;\n\nclass Solution {\npublic:\n    ${retType} ${method_name}(${params}) {\n        // Write your solution here\n        \n    }\n};\n`;
    }

    if (language === 'java') {
        const params = parameters.map(p => `${map[p.type] || 'int'} ${p.name}`).join(', ');
        const retType = map[return_type] || 'int';
        return `import java.util.*;\n\nclass Solution {\n    public ${retType} ${method_name}(${params}) {\n        // Write your solution here\n        \n    }\n}\n`;
    }

    if (language === 'javascript') {
        const params = parameters.map(p => p.name).join(', ');
        const paramDocs = parameters.map(p => ` * @param {${map[p.type] || 'any'}} ${p.name}`).join('\n');
        const retDoc = map[return_type] || 'any';
        return `/**\n${paramDocs}\n * @return {${retDoc}}\n */\nclass Solution {\n    ${method_name}(${params}) {\n        // Write your solution here\n        \n    }\n}\n\nmodule.exports = Solution;\n`;
    }

    return CODE_TEMPLATES[language] || '';
}

// ── Match Status ────────────────────────────────────
export const MATCH_STATUS = {
    PENDING: 'pending',
    ACTIVE: 'active',
    COMPLETED: 'completed',
    CANCELLED: 'cancelled',
};