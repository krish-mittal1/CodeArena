import { useState } from 'react';
import { getCompanyLogoUrl } from '../../utils/companies';

export default function CompanyLogo({ company, size = 'md', roundedClassName = 'rounded-xl', className = '' }) {
    const [hasError, setHasError] = useState(false);
    const logoUrl = getCompanyLogoUrl(company.id);

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
            {logoUrl && !hasError ? (
                <img
                    src={logoUrl}
                    alt={`${company.name} logo`}
                    className="w-[78%] h-[78%] object-contain"
                    loading="lazy"
                    referrerPolicy="no-referrer"
                    onError={() => setHasError(true)}
                />
            ) : (
                <span className="text-lg leading-none" aria-hidden="true">{company.logo}</span>
            )}
        </div>
    );
}
