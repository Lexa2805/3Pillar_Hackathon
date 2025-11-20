'use client';

import { useState, useEffect } from 'react';
import { Sidebar } from '@/app/components/Sidebar';
import { ThemeToggle } from '@/app/components/ThemeToggle';
import { motion } from 'framer-motion';

export default function SettingsPage() {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [user, setUser] = useState<{ name: string; email: string } | null>(null);

    useEffect(() => {
        const userData = localStorage.getItem('user');
        if (userData) {
            setUser(JSON.parse(userData));
        }
    }, []);

    return (
        <div className="flex h-screen bg-gray-50 dark:bg-[#0a0a0a] overflow-hidden transition-colors duration-300">
            <Sidebar isOpen={sidebarOpen} />

            <div className="flex-1 flex flex-col relative min-w-0 z-10">
                <header className="h-16 flex items-center justify-between px-4 sm:px-6 border-b border-gray-200/50 dark:border-white/5 bg-white/50 dark:bg-[#0a0a0a]/50 backdrop-blur-sm">
                    <div className="flex items-center gap-4">
                        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
                        </button>
                        <h1 className="text-lg font-semibold text-gray-900 dark:text-white">Settings</h1>
                    </div>
                    <ThemeToggle />
                </header>

                <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
                    <div className="max-w-2xl mx-auto space-y-8">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
                        >
                            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Profile Settings</h2>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Full Name</label>
                                    <input
                                        type="text"
                                        value={user?.name || ''}
                                        readOnly
                                        className="w-full px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-900 border-none text-gray-500 dark:text-gray-400 cursor-not-allowed"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email Address</label>
                                    <input
                                        type="email"
                                        value={user?.email || ''}
                                        readOnly
                                        className="w-full px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-900 border-none text-gray-500 dark:text-gray-400 cursor-not-allowed"
                                    />
                                </div>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.1 }}
                            className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
                        >
                            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Preferences</h2>
                            <div className="flex items-center justify-between py-4 border-b border-gray-100 dark:border-gray-700 last:border-0">
                                <div>
                                    <h3 className="font-medium text-gray-900 dark:text-white">Theme</h3>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">Toggle between light and dark mode</p>
                                </div>
                                <ThemeToggle />
                            </div>
                        </motion.div>
                    </div>
                </main>
            </div>
        </div>
    );
}
