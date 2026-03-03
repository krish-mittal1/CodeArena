const colorMap = {
    green: 'bg-win/15 text-win border-win/30',
    red: 'bg-loss/15 text-loss border-loss/30',
    yellow: 'bg-draw/15 text-draw border-draw/30',
    purple: 'bg-accent/15 text-accent border-accent/30',
    gray: 'bg-text-muted/15 text-text-secondary border-text-muted/30',
    teal: 'bg-accent/15 text-accent border-accent/30',
};

export default function Badge({ children, color = 'purple', className = '' }) {
    return (
        <span className={`
      inline-flex items-center px-2.5 py-0.5 text-xs font-semibold
      rounded-full border ${colorMap[color]} ${className}
    `}>
            {children}
        </span>
    );
}
