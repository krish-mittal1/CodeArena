import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

export default function Modal({ isOpen, onClose, title, children, size = 'md' }) {
    const sizes = {
        sm: 'max-w-md',
        md: 'max-w-lg',
        lg: 'max-w-2xl',
        xl: 'max-w-4xl',
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[500] flex items-end sm:items-center justify-center p-0 sm:p-4">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
                        onClick={onClose}
                    />
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        transition={{ type: 'spring', duration: 0.4 }}
                        className={`relative w-full ${sizes[size]} max-h-[min(92dvh,900px)] overflow-y-auto bg-bg-elevated border border-border rounded-t-2xl sm:rounded-2xl shadow-2xl`}
                    >
                        {title && (
                            <div className="flex items-center justify-between px-4 sm:px-6 py-4 border-b border-border sticky top-0 bg-bg-elevated z-10">
                                <h3 className="text-lg font-semibold text-text-primary">{title}</h3>
                                <button
                                    onClick={onClose}
                                    className="p-2 min-h-[40px] min-w-[40px] rounded-lg text-text-muted hover:text-text-primary hover:bg-bg-hover transition-colors cursor-pointer flex items-center justify-center"
                                >
                                    <X size={20} />
                                </button>
                            </div>
                        )}
                        <div className="p-4 sm:p-6">{children}</div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
