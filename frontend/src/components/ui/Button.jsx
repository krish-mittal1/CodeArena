import { forwardRef } from 'react';
import { motion } from 'framer-motion';

const variants = {
    primary: 'bg-accent hover:bg-accent-hover text-white border border-accent-hover shadow-md',
    secondary: 'bg-bg-elevated hover:bg-bg-hover text-text-primary border border-border',
    danger: 'bg-loss/15 hover:bg-loss/25 text-loss border border-loss/35',
    ghost: 'hover:bg-bg-elevated text-text-secondary hover:text-text-primary border border-transparent',
};

const sizes = {
    sm: 'px-3 py-1.5 text-sm rounded-[12px_10px_11px_8px]',
    md: 'px-5 py-2.5 text-sm rounded-[15px_12px_14px_10px]',
    lg: 'px-7 py-3 text-base rounded-[18px_14px_16px_12px]',
};

const Button = forwardRef(({ variant = 'primary', size = 'md', children, className = '', disabled, loading, ...props }, ref) => {
    return (
        <button
            ref={ref}
            className={`
        inline-flex items-center justify-center gap-2 font-semibold tracking-[0.01em]
        transition-all duration-200 cursor-pointer
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variants[variant]} ${sizes[size]} ${className}
      `}
            disabled={disabled || loading}
            {...props}
        >
            {loading && (
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
            )}
            {children}
        </button>
    );
});

Button.displayName = 'Button';
export default Button;
