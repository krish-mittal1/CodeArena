import { motion } from 'framer-motion';
import { Settings as SettingsIcon, User, Bell, Shield, Palette, ChevronRight } from 'lucide-react';

export default function Settings() {
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
                    className="flex flex-col items-center text-center"
                >
                    <div className="w-20 h-20 bg-accent/10 rounded-xl flex items-center justify-center border border-accent/20 mb-6">
                        <SettingsIcon size={36} className="text-accent" />
                    </div>
                    <h1 className="text-4xl sm:text-5xl font-extrabold text-text-primary tracking-tight">
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
                    <SettingsSection icon={Palette} title="Appearance" description="Theme and display customization" />
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
            <div className="group flex items-center justify-between p-6 sm:p-7 bg-bg-secondary border border-border rounded-xl hover:bg-bg-elevated hover:border-border-hover transition-colors duration-200 cursor-pointer">
                <div className="flex items-center gap-6">
                    <div className="w-14 h-14 rounded-lg bg-bg-root border border-border flex items-center justify-center group-hover:bg-accent/10 transition-colors duration-200">
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