import { motion } from 'framer-motion';
import { Settings as SettingsIcon, User, Bell, Shield, Palette } from 'lucide-react';

export default function Settings() {
    return (
        <div className="min-h-screen bg-bg-root">
            <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <h1 className="text-3xl font-bold text-text-primary flex items-center gap-3">
                        <SettingsIcon size={28} className="text-accent" />
                        Settings
                    </h1>
                    <p className="text-text-secondary mt-1">Manage your account preferences</p>
                </motion.div>

                <div className="space-y-4">
                    <SettingsSection icon={User} title="Account" description="Manage your username, email, and password" />
                    <SettingsSection icon={Bell} title="Notifications" description="Configure notification preferences" />
                    <SettingsSection icon={Shield} title="Privacy & Security" description="Two-factor authentication and session management" />
                    <SettingsSection icon={Palette} title="Appearance" description="Theme and display customization" />
                </div>
            </div>
        </div>
    );
}

function SettingsSection({ icon: Icon, title, description }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-bg-elevated border border-border rounded-2xl p-5 hover:border-border-hover transition-all cursor-pointer group"
        >
            <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-bg-surface flex items-center justify-center group-hover:bg-accent/10 transition-colors">
                    <Icon size={18} className="text-text-muted group-hover:text-accent transition-colors" />
                </div>
                <div>
                    <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
                    <p className="text-xs text-text-muted mt-0.5">{description}</p>
                </div>
            </div>
        </motion.div>
    );
}
