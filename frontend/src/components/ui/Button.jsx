import { forwardRef } from 'react';
import { motion } from 'framer-motion';

const variants = {
    primary: 'bg-accent hover:bg-accent-hover text-white',
    secondary: 'bg-bg-elevated hover:bg-bg-hover text-text-primary border border-border',
    danger: 'bg-loss/20 hover:bg-loss/30 text-loss border border-loss/30',
    ghost: 'hover:bg-bg-elevated text-text-secondary hover:text-text-primary',
};

const sizes = {
    sm: 'px-3 py-1.5 text-sm rounded-lg',
    md: 'px-5 py-2.5 text-sm rounded-xl',
    lg: 'px-7 py-3 text-base rounded-xl',
};

const Button = forwardRef(({ variant = 'primary', size = 'md', children, className = '', disabled, loading, ...props }, ref) => {
    return (
        <motion.button
            ref={ref}
            whileHover={{ scale: disabled ? 1 : 1.02 }}
            whileTap={{ scale: disabled ? 1 : 0.98 }}
            className={`
        inline-flex items-center justify-center gap-2 font-semibold
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
        </motion.button>
    );
});

Button.displayName = 'Button';
export default Button;
