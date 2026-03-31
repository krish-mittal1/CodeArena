import { useRef, useState, useEffect, useCallback } from 'react';

/**
 * Horizontal resizable split pane.
 *
 * Props:
 *  - left          ReactNode for the left pane
 *  - right         ReactNode for the right pane
 *  - defaultLeft   Initial left pane width as percentage (default 45)
 *  - minLeft       Minimum left pane % (default 25)
 *  - maxLeft       Maximum left pane % (default 65)
 *  - className     Extra classes on the outer wrapper
 */
export default function ResizableSplit({
    left,
    right,
    defaultLeft = 45,
    minLeft = 25,
    maxLeft = 65,
    className = '',
}) {
    const containerRef = useRef(null);
    const [leftPct, setLeftPct] = useState(defaultLeft);
    const isDragging = useRef(false);

    const onMouseDown = useCallback((e) => {
        e.preventDefault();
        isDragging.current = true;
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    }, []);

    useEffect(() => {
        const onMouseMove = (e) => {
            if (!isDragging.current || !containerRef.current) return;
            const rect = containerRef.current.getBoundingClientRect();
            const pct = ((e.clientX - rect.left) / rect.width) * 100;
            setLeftPct(Math.min(maxLeft, Math.max(minLeft, pct)));
        };

        const onMouseUp = () => {
            if (isDragging.current) {
                isDragging.current = false;
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        };

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
        return () => {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };
    }, [minLeft, maxLeft]);

    return (
        <div ref={containerRef} className={`resizable-split ${className}`}>
            {/* Left pane */}
            <div className="resizable-split__left" style={{ width: `${leftPct}%` }}>
                {left}
            </div>

            {/* Drag handle */}
            <div className="resizable-split__handle" onMouseDown={onMouseDown}>
                <div className="resizable-split__handle-line" />
            </div>

            {/* Right pane */}
            <div className="resizable-split__right">
                {right}
            </div>
        </div>
    );
}
