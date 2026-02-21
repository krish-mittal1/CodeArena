export function Skeleton({ className = '', ...props }) {
    return (
        <div
            className={`bg-bg-surface rounded-xl animate-pulse ${className}`}
            {...props}
        />
    );
}

export function StatCardSkeleton() {
    return (
        <div className="bg-bg-elevated border border-border rounded-2xl p-6 space-y-3">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-8 w-28" />
            <Skeleton className="h-3 w-16" />
        </div>
    );
}

export function TableRowSkeleton({ cols = 5 }) {
    return (
        <tr className="border-b border-border/50">
            {Array.from({ length: cols }).map((_, i) => (
                <td key={i} className="py-4 px-4">
                    <Skeleton className="h-4 w-full max-w-[120px]" />
                </td>
            ))}
        </tr>
    );
}

export function ChartSkeleton() {
    return (
        <div className="bg-bg-elevated border border-border rounded-2xl p-6">
            <Skeleton className="h-5 w-40 mb-6" />
            <Skeleton className="h-[250px] w-full rounded-xl" />
        </div>
    );
}
