/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   DSA / LeetCode-style display formatters
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

/** Pretty-print a single JSON-ish line for display. */
export function formatJsonValue(raw) {
    if (raw == null) return '';
    const text = String(raw).trim();
    if (!text) return '';
    try {
        return JSON.stringify(JSON.parse(text));
    } catch {
        return text;
    }
}

/**
 * Format multi-line DSA stdin as LeetCode-style named params:
 *   nums = [2,7,11,15]
 *   target = 9
 */
export function formatDsaInput(rawInput, parameters = []) {
    if (!rawInput && rawInput !== 0) return '';
    const lines = String(rawInput)
        .split('\n')
        .map((line) => line.trimEnd())
        .filter((line, idx, arr) => !(line.trim() === '' && idx === arr.length - 1));

    if (!parameters?.length) {
        return lines.map(formatJsonValue).join('\n');
    }

    return lines
        .map((line, index) => {
            const param = parameters[index];
            const value = formatJsonValue(line);
            if (!param?.name) return value;
            return `${param.name} = ${value}`;
        })
        .join('\n');
}

export function formatDsaOutput(rawOutput, returnType) {
    if (rawOutput == null) return '';
    if (returnType === 'boolean' || returnType === 'bool') {
        return String(rawOutput).trim().toLowerCase();
    }
    return formatJsonValue(rawOutput);
}

/**
 * Normalize description copy toward LeetCode wording (light touch).
 */
export function normalizeLeetCodeText(content) {
    if (!content) return '';
    return String(content)
        .replace(/JSON array/gi, 'array')
        .replace(/\bint\[\]\[\]\b/g, '2D integer array')
        .replace(/\bchar\[\]\[\]\b/g, '2D character grid')
        .replace(/\bstring\[\]\[\]\b/g, '2D string array')
        .replace(/\bint\[\]\b/g, 'integer array')
        .replace(/\bstring\[\]\b/g, 'string array')
        .replace(/\bstr\[\]\b/g, 'string array')
        .replace(/\bstr\b/g, 'string')
        .replace(/\bbool\b/gi, 'boolean')
        .replace(/\s+\((?:int|string|boolean|bool|float|double|long|char)(?:\[\])?(?:\[\])?\)/g, '')
        .trim();
}

/**
 * Build Example[] for UI from API problem payload.
 * Prefers problem.examples; falls back to sample_cases.
 * Never includes hidden tests.
 */
export function buildProblemExamples(problem) {
    if (!problem) return [];

    if (Array.isArray(problem.examples) && problem.examples.length > 0) {
        return problem.examples.map((ex, i) => ({
            key: `ex-${i}`,
            input: ex.input ?? '',
            output: ex.output ?? '',
            explanation: ex.explanation || null,
        }));
    }

    if (Array.isArray(problem.sample_cases) && problem.sample_cases.length > 0) {
        return problem.sample_cases.map((tc, i) => ({
            key: `sample-${tc.order_index ?? i}`,
            input: tc.input ?? '',
            output: tc.expected_output ?? '',
            explanation: tc.explanation || null,
        }));
    }

    return [];
}
