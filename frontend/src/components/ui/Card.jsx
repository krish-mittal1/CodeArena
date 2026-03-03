import { motion } from 'framer-motion';

export default function Card({ children, className = '', glow = false, hover = true, ...props }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            whileHover={hover ? { y: -2, transition: { duration: 0.2 } } : {}}
            className={`
        bg-bg-elevated border border-border rounded-xl p-6
        transition-colors duration-200
        ${hover ? 'hover:border-border-hover' : ''}
        ${glow ? 'border-accent/30' : ''}
        ${className}
      `}
            {...props}
        >
            {children}
        </motion.div>
    );
}
