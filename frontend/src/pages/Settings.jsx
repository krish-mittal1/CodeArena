import { motion } from 'framer-motion';
import { Settings as SettingsIcon, User, Bell, Shield, Palette, ChevronRight } from 'lucide-react';
import { useThemeStore } from '../stores/themeStore';

export default function Settings() {
    const theme = useThemeStore((s) => s.theme);
    const setTheme = useThemeStore((s) => s.setTheme);

    const themeOptions = [
        { id: 'default', label: 'Default', description: 'Current app look and colors' },
        { id: 'dark', label: 'Dark', description: 'High-contrast dark interface' },
        { id: 'light', label: 'Light', description: 'Bright and clean light interface' },
    ];

    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
        }
    };

    return (
        <div className="w-full min-h-[calc(100vh-64px)] bg-bg-root flex flex-col items-center pt-16 sm:pt-20 px-4 pb-24">
            <div className="w-full max-w-3xl flex flex-col gap-12">
                {/* Hero-style Centered Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                    className="paper-card grain-panel flex flex-col items-center text-center px-8 py-12"
                >
                    <div className="w-20 h-20 bg-accent/10 rounded-[22px_18px_20px_14px] flex items-center justify-center border border-accent/20 mb-6 shadow-[4px_4px_0_rgba(0,0,0,0.16)]">
                        <SettingsIcon size={36} className="text-accent" />
                    </div>
                    <p className="editorial-kicker mb-2">Preferences</p>
                    <h1 className="text-4xl sm:text-5xl font-bold text-text-primary tracking-[-0.05em]">
                        Settings
                    </h1>
                    <p className="text-text-secondary font-medium mt-3 text-lg max-w-md">
                        Manage your account preferences and application settings
                    </p>
                </motion.div>

                {/* Settings Cards */}
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="show"
                    className="flex flex-col gap-4"
                >
                    <SettingsSection icon={User} title="Account" description="Manage your username, email, and password" />
                    <SettingsSection icon={Bell} title="Notifications" description="Configure notification preferences" />
                    <SettingsSection icon={Shield} title="Privacy & Security" description="Two-factor authentication and session management" />

                    <motion.div variants={containerVariants} className="paper-card-soft grain-panel p-6 sm:p-7">
                        <div className="flex items-start gap-4 mb-5">
                            <div className="w-12 h-12 rounded-[14px_10px_12px_9px] bg-bg-root border border-border flex items-center justify-center shadow-[2px_2px_0_rgba(0,0,0,0.12)]">
                                <Palette size={20} className="text-accent" />
                            </div>
                            <div>
                                <h3 className="text-lg font-bold text-text-primary tracking-wide">Appearance</h3>
                                <p className="text-sm text-text-muted font-medium mt-1">Theme and display customization</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                            {themeOptions.map((option) => {
                                const active = theme === option.id;
                                return (
                                    <button
                                        key={option.id}
                                        type="button"
                                        onClick={() => setTheme(option.id)}
                                        className={`text-left rounded-[14px_10px_12px_9px] border p-4 transition-colors ${
                                            active
                                                ? 'bg-accent/12 border-accent/40 text-text-primary'
                                                : 'bg-bg-root border-border text-text-secondary hover:border-border-hover hover:bg-bg-hover'
                                        }`}
                                    >
                                        <p className="text-sm font-bold">{option.label}</p>
                                        <p className="text-xs mt-1 opacity-80">{option.description}</p>
                                    </button>
                                );
                            })}
                        </div>
                    </motion.div>
                </motion.div>
            </div>
        </div>
    );
}

function SettingsSection({ icon: Icon, title, description }) {
    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } }
    };

    return (
        <motion.div variants={itemVariants}>
            <div className="group paper-card-soft grain-panel flex items-center justify-between p-6 sm:p-7 hover:bg-bg-elevated hover:border-border-hover transition-colors duration-200 cursor-pointer">
                <div className="flex items-center gap-6">
                    <div className="w-14 h-14 rounded-[16px_12px_14px_10px] bg-bg-root border border-border flex items-center justify-center group-hover:bg-accent/10 transition-colors duration-200 shadow-[2px_2px_0_rgba(0,0,0,0.12)]">
                        <Icon size={24} className="text-text-muted group-hover:text-accent transition-colors duration-200" />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-text-primary tracking-wide">
                            {title}
                        </h3>
                        <p className="text-sm text-text-muted font-medium mt-1">
                            {description}
                        </p>
                    </div>
                </div>
                <div className="pr-2 sm:pr-4">
                    <ChevronRight size={24} className="text-text-muted group-hover:text-text-secondary transition-colors" />
                </div>
            </div>
        </motion.div>
    );
}
