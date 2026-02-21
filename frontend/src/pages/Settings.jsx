import { motion } from 'framer-motion';
import { Settings as SettingsIcon, User, Bell, Shield, Palette, ChevronRight } from 'lucide-react';

export default function Settings() {
    // Animation variants for that premium cascading load effect
    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    return (
        /* THE FIX: Added `flex flex-col items-center` to the outermost div.
           This absolutely guarantees horizontal centering next to your sidebar.
        */
        <div className="w-full min-h-[calc(100vh-64px)] bg-[#09090b] flex flex-col items-center pt-16 sm:pt-20 px-4 pb-24">
            
            {/* The constrained container for the actual content */}
            <div className="w-full max-w-3xl flex flex-col gap-12">
                
                {/* Hero-style Centered Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                    className="flex flex-col items-center text-center"
                >
                    <div className="w-20 h-20 bg-gradient-to-br from-purple-500/20 to-indigo-500/20 rounded-[1.25rem] flex items-center justify-center border border-purple-500/30 shadow-[0_0_30px_rgba(168,85,247,0.15)] mb-6">
                        <SettingsIcon size={36} className="text-purple-400" />
                    </div>
                    <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">
                        Settings
                    </h1>
                    <p className="text-zinc-400 font-medium mt-3 text-lg max-w-md">
                        Manage your account preferences and application settings
                    </p>
                </motion.div>

                {/* Separated Settings Cards with Gaps */}
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="show"
                    className="flex flex-col gap-4"
                >
                    <SettingsSection 
                        icon={User} 
                        title="Account" 
                        description="Manage your username, email, and password" 
                    />
                    <SettingsSection 
                        icon={Bell} 
                        title="Notifications" 
                        description="Configure notification preferences" 
                    />
                    <SettingsSection 
                        icon={Shield} 
                        title="Privacy & Security" 
                        description="Two-factor authentication and session management" 
                    />
                    <SettingsSection 
                        icon={Palette} 
                        title="Appearance" 
                        description="Theme and display customization" 
                    />
                </motion.div>
            </div>
        </div>
    );
}

function SettingsSection({ icon: Icon, title, description }) {
    // Individual card animation
    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } }
    };

    return (
        <motion.div variants={itemVariants}>
            <div 
                className="group flex items-center justify-between p-6 sm:p-7 bg-[#121217] border border-white/5 rounded-2xl hover:bg-[#16161c] hover:border-purple-500/30 hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:shadow-purple-900/10 transition-all duration-300 cursor-pointer"
            >
                <div className="flex items-center gap-6">
                    {/* Floating Icon Container */}
                    <div className="w-14 h-14 rounded-xl bg-[#09090b] border border-white/5 flex items-center justify-center group-hover:border-purple-500/40 group-hover:bg-purple-500/10 transition-all duration-300 shadow-inner">
                        <Icon size={24} className="text-zinc-500 group-hover:text-purple-400 transition-colors duration-300" />
                    </div>
                    
                    {/* Text Details */}
                    <div>
                        <h3 className="text-lg font-bold text-white tracking-wide group-hover:text-purple-50 transition-colors duration-300">
                            {title}
                        </h3>
                        <p className="text-sm text-zinc-500 font-medium mt-1 group-hover:text-zinc-400 transition-colors duration-300">
                            {description}
                        </p>
                    </div>
                </div>

                {/* Animated Chevron */}
                <div className="pr-2 sm:pr-4">
                    <ChevronRight size={24} className="text-zinc-600 group-hover:text-purple-400 group-hover:translate-x-1.5 transition-all duration-300" />
                </div>
            </div>
        </motion.div>
    );
}