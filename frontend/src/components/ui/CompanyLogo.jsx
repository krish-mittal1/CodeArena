import { useState } from 'react';

export default function CompanyLogo({ company, size = 'md', roundedClassName = 'rounded-xl', className = '' }) {
    const [sourceIndex, setSourceIndex] = useState(0);
    const logoSources = [
        `/company-logos/${company.id}.png`,
        `/company-logos/${company.id}.svg`,
        `/company-logos/${company.id}.jpg`,
    ];
    const activeSource = logoSources[sourceIndex];
    const hasExhaustedSources = sourceIndex >= logoSources.length;

    const sizeClassName = size === 'lg'
        ? 'w-16 h-16'
        : size === 'sm'
            ? 'w-9 h-9'
            : 'w-11 h-11';

    return (
        <div
            className={`${sizeClassName} ${roundedClassName} flex items-center justify-center overflow-hidden shrink-0 ${className}`}
            style={{ backgroundColor: `${company.color}15` }}
        >
            {!hasExhaustedSources ? (
                <img
                    src={activeSource}
                    alt={`${company.name} logo`}
                    className="w-[78%] h-[78%] object-contain"
                    loading="lazy"
                    onError={() => setSourceIndex((prev) => prev + 1)}
                />
            ) : (
                <span className="text-lg leading-none" aria-hidden="true">{company.logo}</span>
            )}
        </div>
    );
}
