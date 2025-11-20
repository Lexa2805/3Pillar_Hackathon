'use client';

import { useState } from 'react';
import { Sidebar } from '@/app/components/Sidebar';
import { ThemeToggle } from '@/app/components/ThemeToggle';
import { motion } from 'framer-motion';

export default function HelpPage() {
    const [sidebarOpen, setSidebarOpen] = useState(true);

    const faqs = [
        {
            question: "How do I start a new session?",
            answer: "Click on the 'New Session' button in the dashboard or sidebar. Enter your initial idea or problem statement to get started."
        },
        {
            question: "What are the different agents?",
            answer: "We have three main agents: The Idea Agent generates creative solutions, the Critic Agent evaluates them for feasibility, and the Builder Agent helps plan the implementation."
        },
        {
            question: "Can I talk to a specific agent?",
            answer: "Yes! In the session view, you can select a specific agent (Idea, Critic, or Builder) from the toolbar to have a one-on-one conversation."
        },
        {
            question: "How is my data used?",
            answer: "Your sessions are private and only accessible to you. We use the data solely to generate responses within your session context."
        }
    ];

    return (
        <div className="flex h-screen bg-gray-50 dark:bg-[#0a0a0a] overflow-hidden transition-colors duration-300">
            <Sidebar isOpen={sidebarOpen} />

            <div className="flex-1 flex flex-col relative min-w-0 z-10">
                <header className="h-16 flex items-center justify-between px-4 sm:px-6 border-b border-gray-200/50 dark:border-white/5 bg-white/50 dark:bg-[#0a0a0a]/50 backdrop-blur-sm">
                    <div className="flex items-center gap-4">
                        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
                        </button>
                        <h1 className="text-lg font-semibold text-gray-900 dark:text-white">Help & Support</h1>
                    </div>
                    <ThemeToggle />
                </header>

                <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
                    <div className="max-w-3xl mx-auto space-y-8">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="text-center mb-12"
                        >
                            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">How can we help you?</h2>
                            <p className="text-lg text-gray-600 dark:text-gray-400">
                                Find answers to common questions and learn how to get the most out of LuminosityTeam.
                            </p>
                        </motion.div>

                        <div className="grid gap-6">
                            {faqs.map((faq, idx) => (
                                <motion.div
                                    key={idx}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: idx * 0.1 }}
                                    className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
                                >
                                    <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">{faq.question}</h3>
                                    <p className="text-gray-600 dark:text-gray-400 leading-relaxed">{faq.answer}</p>
                                </motion.div>
                            ))}
                        </div>

                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.5 }}
                            className="bg-purple-50 dark:bg-purple-900/20 rounded-2xl p-8 text-center mt-12"
                        >
                            <h3 className="text-xl font-bold text-purple-900 dark:text-purple-100 mb-2">Still need help?</h3>
                            <p className="text-purple-700 dark:text-purple-300 mb-6">
                                Contact our support team for further assistance.
                            </p>
                            <button className="px-6 py-3 bg-purple-600 text-white rounded-xl font-medium hover:bg-purple-700 transition-colors shadow-lg shadow-purple-500/20">
                                Contact Support
                            </button>
                        </motion.div>
                    </div>
                </main>
            </div>
        </div>
    );
}
