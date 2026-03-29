export default function Card({ children, className = '', glow = false, hover = true, ...props }) {
    return (
        <div
            className={`
        paper-card p-6
        transition-colors duration-200
        ${hover ? 'hover:border-border-hover' : ''}
        ${glow ? 'border-accent/40' : ''}
        ${className}
      `}
            {...props}
        >
            {children}
        </div>
    );
}
