'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { ThemeToggle } from '@/app/components/ThemeToggle';
import { Sidebar } from '@/app/components/Sidebar';
import toast from 'react-hot-toast';

// Mock agents for now
const AVAILABLE_AGENTS = [
    {
        id: 'researcher',
        name: 'Researcher',
        role: 'Information Gatherer',
        description: 'Searches the web and gathers relevant facts and data.',
        icon: (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
        ),
        color: 'blue'
    },
    {
        id: 'creative',
        name: 'Creative',
        role: 'Idea Generator',
        description: 'Proposes innovative and out-of-the-box solutions.',
        icon: (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
        ),
        color: 'purple'
    },
    {
        id: 'critic',
        name: 'Critic',
        role: 'Evaluator',
        description: 'Analyzes ideas for feasibility and potential issues.',
        icon: (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        ),
        color: 'red'
    }
];

export default function NewSessionPage() {
    const router = useRouter();
    const [message, setMessage] = useState('');
    const [selectedAgents] = useState<string[]>(['researcher', 'creative', 'critic']);
    const [loading, setLoading] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(true);



    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!message.trim()) {
            toast.error('Please enter a message');
            return;
        }
        if (selectedAgents.length === 0) {
            toast.error('Please select at least one agent');
            return;
        }

        setLoading(true);

        try {
            // Get user from localStorage
            const storedUser = localStorage.getItem('user');
            const user = storedUser ? JSON.parse(storedUser) : null;

            // Create session
            const res = await fetch('http://localhost:8000/api/sessions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: message.slice(0, 50) + (message.length > 50 ? '...' : ''),
                    description: 'Brainstorming session',
                    user_email: user ? user.email : undefined
                })
            });

            if (!res.ok) throw new Error('Failed to create session');

            const session = await res.json();

            toast.success('Session started!');
            router.push(`/sessions/${session.session_id}?prompt=${encodeURIComponent(message)}`);
        } catch (error) {
            console.error(error);
            toast.error('Failed to start session');
            setLoading(false);
        }
    }; return (
        <div className="flex h-screen bg-gray-50 dark:bg-[#0a0a0a] overflow-hidden transition-colors duration-300">
            {/* Ambient Background Effects */}
            <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
                <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-purple-500/5 blur-[120px] animate-pulse" />
                <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-500/5 blur-[120px] animate-pulse delay-1000" />
            </div>

            {/* Sidebar */}
            <Sidebar isOpen={sidebarOpen} />

            {/* Main Content */}
            <div className="flex-1 flex flex-col relative min-w-0 z-10">
                {/* Header */}
                <header className="h-16 flex items-center justify-between px-4 sm:px-6 border-b border-gray-200/50 dark:border-white/5 bg-white/50 dark:bg-[#0a0a0a]/50 backdrop-blur-sm">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            className="p-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        </button>
                        <h1 className="text-lg font-semibold text-gray-900 dark:text-white hidden sm:block">New Session</h1>
                    </div>
                    <div className="flex items-center gap-2">
                        <ThemeToggle />
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 flex flex-col items-center justify-center min-h-[calc(100vh-4rem)]">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="w-full max-w-3xl space-y-8"
                    >
                        <div className="text-center space-y-4 mb-12">
                            <h2 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-blue-600 dark:from-purple-400 dark:to-blue-400">
                                What can we help you solve?
                            </h2>
                            <p className="text-lg text-gray-600 dark:text-gray-400">
                                Assemble your AI team and start brainstorming.
                            </p>
                        </div>

                        {/* Agents Selection */}
                        <div className="bg-white/40 dark:bg-gray-800/40 backdrop-blur-md rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                            <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
                                This is your team
                            </h3>
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                                {AVAILABLE_AGENTS.map((agent) => (
                                    <motion.div
                                        key={agent.id}
                                        whileHover={{ scale: 1.02 }}
                                        className="relative p-4 rounded-xl border-2 text-left transition-all border-purple-500 bg-purple-50 dark:bg-purple-900/20"
                                    >
                                        <div className="flex items-center gap-3 mb-2">
                                            <div className="p-2 rounded-lg bg-purple-100 text-purple-600 dark:bg-purple-900/50 dark:text-purple-300">
                                                {agent.icon}
                                            </div>
                                            <span className="font-bold text-gray-900 dark:text-white">{agent.name}</span>
                                        </div>
                                        <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2">{agent.description}</p>
                                    </motion.div>
                                ))}
                            </div>
                        </div>

                        {/* Chat Input */}
                        <form onSubmit={handleSubmit} className="relative">
                            <div className="relative group">
                                <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
                                <div className="relative bg-white dark:bg-gray-900 rounded-2xl shadow-xl">
                                    <textarea
                                        value={message}
                                        onChange={(e) => setMessage(e.target.value)}
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter' && !e.shiftKey) {
                                                e.preventDefault();
                                                handleSubmit(e);
                                            }
                                        }}
                                        placeholder="Describe your idea, ask a question, or paste a link..."
                                        className="w-full p-6 pr-16 bg-transparent border-none focus:ring-0 text-gray-900 dark:text-white placeholder-gray-400 text-lg resize-none min-h-[120px] rounded-2xl"
                                    />
                                    <div className="absolute bottom-4 right-4 flex items-center gap-2">
                                        <motion.button
                                            whileHover={{ scale: 1.1 }}
                                            whileTap={{ scale: 0.9 }}
                                            type="submit"
                                            disabled={loading || !message.trim()}
                                            className="p-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            {loading ? (
                                                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                            ) : (
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                                </svg>
                                            )}
                                        </motion.button>
                                    </div>
                                </div>
                            </div>
                            <p className="text-center text-xs text-gray-400 mt-4">
                                Press Enter to start session • Shift + Enter for new line
                            </p>
                        </form>
                    </motion.div>
                </main>
            </div>
        </div>
    );
}
