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

// ── Default code templates ──────────────────────────
export const CODE_TEMPLATES = {
    python: `# Write your solution here\nimport sys\ninput = sys.stdin.readline\n\ndef solve():\n    pass\n\nsolve()\n`,
    cpp: `#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios_base::sync_with_stdio(false);\n    cin.tie(NULL);\n    \n    return 0;\n}\n`,
    java: `import java.util.*;\n\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        \n    }\n}\n`,
    javascript: `// Read input line by line\nconst lines = [];\nlet currentLine = 0;\n\n// For browser/node environments - read from stdin\nprocess.stdin.setEncoding('utf8');\nprocess.stdin.on('data', (chunk) => {\n    const inputLines = chunk.trim().split('\\n');\n    lines.push(...inputLines);\n});\n\nprocess.stdin.on('end', () => {\n    // solve here\n    // Access input via: lines[currentLine++]\n});\n`,
};

// ── Match Status ────────────────────────────────────
export const MATCH_STATUS = {
    PENDING: 'pending',
    ACTIVE: 'active',
    COMPLETED: 'completed',
    CANCELLED: 'cancelled',
};