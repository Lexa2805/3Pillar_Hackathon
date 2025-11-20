'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

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
                        <div key={session.session_id} className="relative group/item">
                            <Link
                                href={`/sessions/${session.session_id}`}
                                className={`w-full text-left px-3 py-2 pr-10 rounded-lg text-sm transition-colors flex flex-col gap-0.5 ${pathname === `/sessions/${session.session_id}`
                                    ? 'bg-gray-100 dark:bg-gray-800 text-purple-600 dark:text-purple-400'
                                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800/50'
                                    }`}
                            >
                                <span className="font-medium truncate">{session.title}</span>
                                <span className="text-xs text-gray-400">
                                    {new Date(session.updated_at).toLocaleDateString()}
                                </span>
                            </Link>
                            <button
                                onClick={(e) => {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    toast((t) => (
                                        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 p-6 min-w-[320px]">
                                            <div className="flex items-center gap-3 mb-4">
                                                <div className="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center flex-shrink-0">
                                                    <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                                    </svg>
                                                </div>
                                                <div className="flex-1">
                                                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Delete Session</h3>
                                                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Are you sure you want to delete this session?</p>
                                                </div>
                                            </div>
                                            <div className="flex gap-3 justify-end">
                                                <button
                                                    onClick={() => toast.dismiss(t.id)}
                                                    className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                                                >
                                                    Cancel
                                                </button>
                                                <button
                                                    onClick={async () => {
                                                        toast.dismiss(t.id);
                                                        try {
                                                            const res = await fetch(`http://localhost:8000/api/sessions/${session.session_id}`, {
                                                                method: 'DELETE'
                                                            });
                                                            if (res.ok) {
                                                                setSessions(sessions.filter(s => s.session_id !== session.session_id));
                                                                toast.success('Session deleted');
                                                            } else {
                                                                toast.error('Failed to delete session');
                                                            }
                                                        } catch (error) {
                                                            console.error('Failed to delete session', error);
                                                            toast.error('Failed to delete session');
                                                        }
                                                    }}
                                                    className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </div>
                                    ), {
                                        duration: Infinity,
                                        position: 'top-center',
                                        style: {
                                            background: 'transparent',
                                            boxShadow: 'none',
                                            padding: 0,
                                        },
                                    });
                                }}
                                className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 opacity-0 group-hover/item:opacity-100 text-gray-400 hover:text-red-600 dark:hover:text-red-400 rounded transition-all"
                                title="Delete session"
                            >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </button>
                        </div>
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
