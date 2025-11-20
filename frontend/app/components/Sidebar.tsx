'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';

interface Session {
    session_id: string;
    title: string;
    updated_at: string;
}

export function Sidebar({ isOpen }: { isOpen: boolean }) {
    const pathname = usePathname();
    const [sessions, setSessions] = useState<Session[]>([]);
    const [user, setUser] = useState<{ id: string; email: string; name?: string } | null>(null);

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            const parsedUser = JSON.parse(storedUser);
            setUser(parsedUser);
            fetchSessions(parsedUser.email);
        } else {
            fetchSessions();
        }
    }, []);

    const fetchSessions = async (userEmail?: string) => {
        try {
            const url = userEmail
                ? `http://localhost:8000/api/sessions?user_email=${encodeURIComponent(userEmail)}`
                : 'http://localhost:8000/api/sessions';

            const res = await fetch(url);
            if (res.ok) {
                const data = await res.json();
                setSessions(data);
            }
        } catch (error) {
            console.error('Failed to fetch sessions', error);
        }
    };

    return (
        <motion.aside
            initial={{ width: 280, opacity: 1 }}
            animate={{
                width: isOpen ? 280 : 0,
                opacity: isOpen ? 1 : 0
            }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-r border-gray-200 dark:border-gray-800 flex-shrink-0 overflow-hidden relative z-20 hidden md:flex flex-col"
        >
            <div className="p-4 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between">
                <Link href="/dashboard" className="flex items-center gap-2 text-gray-900 dark:text-white font-bold">
                    <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg flex items-center justify-center text-white text-sm">
                        L
                    </div>
                    <span>Luminosity</span>
                </Link>
            </div>

            <div className="p-4 flex-1 overflow-y-auto">
                <div className="mb-6">
                    <Link href="/sessions/new" className="w-full flex items-center gap-2 px-4 py-3 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 rounded-xl font-medium hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        New Session
                    </Link>
                </div>

                <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3 px-2">
                    Recent Sessions
                </h3>
                <div className="space-y-1">
                    {sessions.map((session) => (
                        <Link
                            key={session.session_id}
                            href={`/sessions/${session.session_id}`}
                            className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex flex-col gap-0.5 group ${pathname === `/sessions/${session.session_id}`
                                ? 'bg-gray-100 dark:bg-gray-800 text-purple-600 dark:text-purple-400'
                                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800/50'
                                }`}
                        >
                            <span className="font-medium truncate">{session.title}</span>
                            <span className="text-xs text-gray-400">
                                {new Date(session.updated_at).toLocaleDateString()}
                            </span>
                        </Link>
                    ))}
                </div>
            </div>

            <div className="p-4 border-t border-gray-200 dark:border-gray-800">
                <div className="flex items-center gap-3 px-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center text-white text-xs font-bold">
                        {user ? (user.name ? user.name[0].toUpperCase() : user.email[0].toUpperCase()) : 'U'}
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                            {user ? (user.name || user.email.split('@')[0]) : 'Guest'}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                            {user ? user.email : 'Please log in'}
                        </p>
                    </div>
                </div>
            </div>
        </motion.aside>
    );
}
