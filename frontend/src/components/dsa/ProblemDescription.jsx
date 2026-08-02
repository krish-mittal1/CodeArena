import { normalizeLeetCodeText } from '../../utils/dsaFormat';

/**
 * Escape HTML entities so user/problem text cannot inject markup.
 */
function escapeHtml(text) {
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

/**
 * Safe inline markdown: **bold**, *italic*, `code`. No raw HTML.
 * Applied after HTML escaping.
 */
function renderInline(text) {
    const escaped = escapeHtml(text);
    return escaped
        .replace(/`([^`]+)`/g, '<code class="px-1 py-0.5 rounded-[3px] bg-bg-root/80 border border-border/60 font-mono text-[0.9em] text-text-primary">$1</code>')
        .replace(/\*\*([^*]+)\*\*/g, '<strong class="font-semibold text-text-primary">$1</strong>')
        .replace(/(^|[^*\w])\*([^*\n]+)\*(?!\*)/g, '$1<em class="italic text-text-secondary">$2</em>');
}

function Inline({ text }) {
    return (
        <span
            dangerouslySetInnerHTML={{ __html: renderInline(text) }}
        />
    );
}

/**
 * Parse description into blocks: headings, lists, paragraphs.
 * Keeps XSS-safe (escaped + limited inline tags only).
 */
function parseBlocks(raw) {
    const lines = String(raw || '').replace(/\r\n/g, '\n').split('\n');
    const blocks = [];
    let i = 0;

    while (i < lines.length) {
        const line = lines[i];
        const trimmed = line.trim();

        if (!trimmed) {
            i += 1;
            continue;
        }

        const heading = trimmed.match(/^(#{1,3})\s+(.+)$/);
        if (heading) {
            blocks.push({ type: 'heading', level: heading[1].length, text: heading[2] });
            i += 1;
            continue;
        }

        if (/^[-*•]\s+/.test(trimmed)) {
            const items = [];
            while (i < lines.length && /^[-*•]\s+/.test(lines[i].trim())) {
                items.push(lines[i].trim().replace(/^[-*•]\s+/, ''));
                i += 1;
            }
            blocks.push({ type: 'ul', items });
            continue;
        }

        if (/^\d+\.\s+/.test(trimmed)) {
            const items = [];
            while (i < lines.length && /^\d+\.\s+/.test(lines[i].trim())) {
                items.push(lines[i].trim().replace(/^\d+\.\s+/, ''));
                i += 1;
            }
            blocks.push({ type: 'ol', items });
            continue;
        }

        // Paragraph: gather until blank line or special block
        const paraLines = [trimmed];
        i += 1;
        while (i < lines.length) {
            const next = lines[i].trim();
            if (!next) break;
            if (/^(#{1,3})\s+/.test(next)) break;
            if (/^[-*•]\s+/.test(next)) break;
            if (/^\d+\.\s+/.test(next)) break;
            paraLines.push(next);
            i += 1;
        }
        blocks.push({ type: 'p', text: paraLines.join(' ') });
    }

    return blocks;
}

const headingClass = {
    1: 'text-base font-bold text-text-primary mt-1',
    2: 'text-sm font-semibold text-text-primary mt-1',
    3: 'text-sm font-semibold text-text-secondary mt-1',
};

/**
 * Light typography for problem statements: paragraphs, lists, headings,
 * inline code/bold, constraints lists, optional embedded images.
 */
export default function ProblemDescription({ problem, showIoFormats = false }) {
    if (!problem) return null;

    const images = Array.isArray(problem.images) ? problem.images : [];
    const description = normalizeLeetCodeText(problem.description);
    const constraints = problem.constraints
        ? normalizeLeetCodeText(problem.constraints)
        : null;

    const blocks = parseBlocks(description);

    return (
        <div className="space-y-5">
            <div className="space-y-3">
                {blocks.map((block, i) => {
                    if (block.type === 'heading') {
                        const Tag = `h${Math.min(block.level + 2, 6)}`;
                        return (
                            <Tag key={i} className={headingClass[block.level] || headingClass[2]}>
                                <Inline text={block.text} />
                            </Tag>
                        );
                    }
                    if (block.type === 'ul') {
                        return (
                            <ul
                                key={i}
                                className="space-y-1.5 text-sm text-text-secondary leading-relaxed list-disc pl-5 marker:text-text-muted"
                            >
                                {block.items.map((item, j) => (
                                    <li key={j} className="pl-1">
                                        <Inline text={item} />
                                    </li>
                                ))}
                            </ul>
                        );
                    }
                    if (block.type === 'ol') {
                        return (
                            <ol
                                key={i}
                                className="space-y-1.5 text-sm text-text-secondary leading-relaxed list-decimal pl-5 marker:text-text-muted"
                            >
                                {block.items.map((item, j) => (
                                    <li key={j} className="pl-1">
                                        <Inline text={item} />
                                    </li>
                                ))}
                            </ol>
                        );
                    }
                    return (
                        <p key={i} className="text-sm text-text-secondary leading-relaxed">
                            <Inline text={block.text} />
                        </p>
                    );
                })}
            </div>

            {images.length > 0 && (
                <div className="space-y-3">
                    {images.map((img, i) => (
                        <figure key={`${img.src}-${i}`} className="space-y-2">
                            <div className="overflow-hidden border border-border bg-bg-surface/40 rounded-[6px]">
                                <img
                                    src={img.src}
                                    alt={img.alt || `${problem.title} diagram`}
                                    className="w-full max-h-64 object-contain bg-[#1a1612]"
                                    loading="lazy"
                                />
                            </div>
                            {img.alt && (
                                <figcaption className="text-xs text-text-muted text-center">
                                    {img.alt}
                                </figcaption>
                            )}
                        </figure>
                    ))}
                </div>
            )}

            {showIoFormats && problem.input_format && (
                <div>
                    <h3 className="text-sm font-semibold text-text-primary mb-2">Input</h3>
                    <p className="text-sm text-text-secondary leading-relaxed whitespace-pre-wrap">
                        {normalizeLeetCodeText(problem.input_format)}
                    </p>
                </div>
            )}

            {showIoFormats && problem.output_format && (
                <div>
                    <h3 className="text-sm font-semibold text-text-primary mb-2">Output</h3>
                    <p className="text-sm text-text-secondary leading-relaxed whitespace-pre-wrap">
                        {normalizeLeetCodeText(problem.output_format)}
                    </p>
                </div>
            )}

            {constraints && (
                <div>
                    <h3 className="text-sm font-semibold text-text-primary mb-2">Constraints</h3>
                    <ul className="space-y-1.5 text-sm text-text-secondary font-mono leading-relaxed list-disc pl-5 marker:text-text-muted">
                        {constraints.split('\n').map((line) => line.trim()).filter(Boolean).map((line, i) => (
                            <li key={i} className="pl-1">
                                <Inline text={line.replace(/^[-*•]\s*/, '')} />
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}
