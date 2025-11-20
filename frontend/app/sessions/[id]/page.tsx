'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ThemeToggle } from '@/app/components/ThemeToggle';
import { Sidebar } from '@/app/components/Sidebar';
import { ProjectPlanView, ProjectPlan } from '@/app/components/ProjectPlanView';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';

interface AgentResponse {
    idea_response: string;
    critic_response: string;
    builder_response: string | ProjectPlan;
}

interface Message {
    agent: string;
    content: string | ProjectPlan;
    timestamp: string;
}

export default function SessionPage() {
    const params = useParams();
    const searchParams = useSearchParams();
    const sessionId = params.id as string;
    const initialPrompt = searchParams.get('prompt');

    const [loading, setLoading] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [currentStep, setCurrentStep] = useState<'idle' | 'idea' | 'critic' | 'builder'>('idle');
    const [inputMessage, setInputMessage] = useState('');
    const [selectedAgent, setSelectedAgent] = useState<string>('all');
    const [sessionTitle, setSessionTitle] = useState<string>('');
    const [isEditingTitle, setIsEditingTitle] = useState(false);
    const [editedTitle, setEditedTitle] = useState('');

    const hasFetched = useRef(false);

    useEffect(() => {
        if (initialPrompt && !hasFetched.current) {
            hasFetched.current = true;
            runBrainstorm(initialPrompt);
        } else {
            fetchSession();
        }
    }, [sessionId, initialPrompt]);

    const fetchSession = async () => {
        try {
            const res = await fetch(`http://localhost:8000/api/sessions/${sessionId}`);
            if (!res.ok) throw new Error('Failed to load session');
            const data = await res.json();
            setMessages(data.messages || []);
            setSessionTitle(data.title || '');
            setEditedTitle(data.title || '');
        } catch (error) {
            console.error(error);
            toast.error('Could not load session history');
        }
    };

    const handleTitleUpdate = async () => {
        if (!editedTitle.trim() || editedTitle === sessionTitle) {
            setIsEditingTitle(false);
            return;
        }

        try {
            const res = await fetch(`http://localhost:8000/api/sessions/${sessionId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: editedTitle })
            });

            if (!res.ok) throw new Error('Failed to update title');

            setSessionTitle(editedTitle);
            setIsEditingTitle(false);
            toast.success('Session renamed');
        } catch (error) {
            console.error(error);
            toast.error('Failed to rename session');
        }
    };

    const runBrainstorm = async (prompt: string) => {
        setLoading(true);

        // Add user message immediately
        setMessages(prev => [...prev, { agent: 'user', content: prompt, timestamp: new Date().toISOString() }]);

        try {
            if (selectedAgent === 'all') {
                setCurrentStep('idea');
                const res = await fetch('http://localhost:8000/api/brainstorm', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: prompt,
                        session_id: sessionId
                    })
                });

                if (!res.ok) {
                    const errorData = await res.json().catch(() => ({}));
                    console.error('Brainstorming error details:', errorData);
                    throw new Error(errorData.detail || 'Brainstorming failed');
                }

                const data: AgentResponse = await res.json();

                // Simulate streaming/progressive reveal
                setCurrentStep('critic');
                await new Promise(r => setTimeout(r, 1000));

                setCurrentStep('builder');
                await new Promise(r => setTimeout(r, 1000));

                setCurrentStep('idle');
                setLoading(false);

                setMessages(prev => [
                    ...prev,
                    { agent: 'idea', content: data.idea_response, timestamp: new Date().toISOString() },
                    { agent: 'critic', content: data.critic_response, timestamp: new Date().toISOString() },
                    { agent: 'builder', content: data.builder_response, timestamp: new Date().toISOString() }
                ]);
            } else {
                // Chat with specific agent
                setCurrentStep(selectedAgent as any);
                const res = await fetch('http://localhost:8000/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: prompt,
                        session_id: sessionId,
                        target_agent: selectedAgent
                    })
                });

                if (!res.ok) throw new Error('Chat failed');

                const data = await res.json();
                setLoading(false);
                setCurrentStep('idle');

                setMessages(prev => [
                    ...prev,
                    { agent: data.agent, content: data.response, timestamp: new Date().toISOString() }
                ]);
            }

        } catch (error) {
            console.error(error);
            toast.error('Something went wrong with the agents');
            setLoading(false);
            setCurrentStep('idle');
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputMessage.trim() || loading) return;

        const prompt = inputMessage;
        setInputMessage('');
        await runBrainstorm(prompt);
    };

    const getAgentIcon = (agent: string) => {
        switch (agent) {
            case 'idea':
                return (
                    <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400 flex items-center justify-center">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
                    </div>
                );
            case 'critic':
                return (
                    <div className="w-8 h-8 rounded-lg bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400 flex items-center justify-center">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    </div>
                );
            case 'builder':
                return (
                    <div className="w-8 h-8 rounded-lg bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400 flex items-center justify-center">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                    </div>
                );
            default:
                return (
                    <div className="w-8 h-8 rounded-lg bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 flex items-center justify-center">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                    </div>
                );
        }
    };

    const getAgentName = (agent: string) => {
        switch (agent) {
            case 'idea': return 'Idea Agent';
            case 'critic': return 'Critic Agent';
            case 'builder': return 'Builder Agent';
            case 'user': return 'You';
            default: return 'System';
        }
    };

    return (
        <div className="flex h-screen bg-gray-50 dark:bg-[#0a0a0a] overflow-hidden transition-colors duration-300">
            {/* Sidebar */}
            <Sidebar isOpen={sidebarOpen} />

            {/* Main Content */}
            <div className="flex-1 flex flex-col relative min-w-0 z-10">
                <header className="h-16 flex items-center justify-between px-4 sm:px-6 border-b border-gray-200/50 dark:border-white/5 bg-white/50 dark:bg-[#0a0a0a]/50 backdrop-blur-sm">
                    <div className="flex items-center gap-4 flex-1">
                        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
                        </button>
                        {isEditingTitle ? (
                            <input
                                type="text"
                                value={editedTitle}
                                onChange={(e) => setEditedTitle(e.target.value)}
                                onBlur={handleTitleUpdate}
                                onKeyDown={(e) => e.key === 'Enter' && handleTitleUpdate()}
                                autoFocus
                                className="text-lg font-semibold text-gray-900 dark:text-white bg-transparent border-b border-purple-500 focus:outline-none w-full max-w-md"
                            />
                        ) : (
                            <h1
                                onClick={() => {
                                    setEditedTitle(sessionTitle);
                                    setIsEditingTitle(true);
                                }}
                                className="text-lg font-semibold text-gray-900 dark:text-white cursor-pointer hover:text-purple-600 dark:hover:text-purple-400 transition-colors truncate max-w-md"
                                title="Click to rename"
                            >
                                {sessionTitle || `Session ${sessionId.slice(0, 8)}...`}
                            </h1>
                        )}
                    </div>
                    <ThemeToggle />
                </header>

                <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
                    <div className="max-w-4xl mx-auto space-y-8 pb-24">
                        {messages.map((msg, idx) => (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.5 }}
                                className={`flex gap-4 ${msg.agent === 'user' ? 'flex-row-reverse' : ''}`}
                            >
                                <div className="flex-shrink-0 mt-1">
                                    {getAgentIcon(msg.agent)}
                                </div>
                                <div className={`flex-1 max-w-3xl ${msg.agent === 'user' ? 'text-right' : ''}`}>
                                    <div className="flex items-center gap-2 mb-1 text-sm text-gray-500 dark:text-gray-400">
                                        <span className="font-medium">{getAgentName(msg.agent)}</span>
                                        <span>•</span>
                                        <span>{new Date(msg.timestamp).toLocaleTimeString()}</span>
                                    </div>
                                    <div className={`p-6 rounded-2xl shadow-sm border ${msg.agent === 'user'
                                        ? 'bg-purple-600 text-white border-purple-500'
                                        : 'bg-white dark:bg-gray-800 border-gray-100 dark:border-gray-700 text-gray-800 dark:text-gray-200'
                                        }`}>
                                        {(() => {
                                            if (msg.agent === 'builder') {
                                                let plan: ProjectPlan | null = null;
                                                if (typeof msg.content === 'object' && msg.content !== null) {
                                                    plan = msg.content as ProjectPlan;
                                                } else if (typeof msg.content === 'string') {
                                                    try {
                                                        if (msg.content.trim().startsWith('{')) {
                                                            const parsed = JSON.parse(msg.content);
                                                            if (parsed.stories && parsed.tasks) {
                                                                plan = parsed;
                                                            }
                                                        }
                                                    } catch (e) {
                                                        // Not JSON
                                                    }
                                                }

                                                if (plan) {
                                                    return <ProjectPlanView plan={plan} />;
                                                }
                                            }

                                            return (
                                                <div className="prose dark:prose-invert max-w-none">
                                                    <ReactMarkdown>
                                                        {typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}
                                                    </ReactMarkdown>
                                                </div>
                                            );
                                        })()}
                                    </div>
                                </div>
                            </motion.div>
                        ))}

                        {loading && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="flex gap-4"
                            >
                                <div className="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center animate-pulse">
                                    <div className="w-4 h-4 bg-gray-400 rounded-full" />
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="text-sm font-medium text-purple-600 dark:text-purple-400 animate-pulse">
                                            {currentStep === 'idea' && 'Idea Agent is thinking...'}
                                            {currentStep === 'critic' && 'Critic Agent is reviewing...'}
                                            {currentStep === 'builder' && 'Builder Agent is planning...'}
                                        </span>
                                    </div>
                                    <div className="h-24 bg-gray-100 dark:bg-gray-800/50 rounded-2xl animate-pulse" />
                                </div>
                            </motion.div>
                        )}
                    </div>
                </main>

                <div className="p-4 bg-white dark:bg-[#0a0a0a] border-t border-gray-200 dark:border-gray-800">
                    <div className="max-w-4xl mx-auto space-y-4">
                        {/* Agent Selector */}
                        <div className="flex gap-2 overflow-x-auto pb-2">
                            <button
                                onClick={() => setSelectedAgent('all')}
                                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap ${selectedAgent === 'all'
                                    ? 'bg-purple-600 text-white'
                                    : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                                    }`}
                            >
                                All Agents
                            </button>
                            <button
                                onClick={() => setSelectedAgent('idea')}
                                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap flex items-center gap-2 ${selectedAgent === 'idea'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                                    }`}
                            >
                                <span className="w-2 h-2 rounded-full bg-blue-400"></span>
                                Idea Agent
                            </button>
                            <button
                                onClick={() => setSelectedAgent('critic')}
                                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap flex items-center gap-2 ${selectedAgent === 'critic'
                                    ? 'bg-red-600 text-white'
                                    : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                                    }`}
                            >
                                <span className="w-2 h-2 rounded-full bg-red-400"></span>
                                Critic Agent
                            </button>
                            <button
                                onClick={() => setSelectedAgent('builder')}
                                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap flex items-center gap-2 ${selectedAgent === 'builder'
                                    ? 'bg-green-600 text-white'
                                    : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                                    }`}
                            >
                                <span className="w-2 h-2 rounded-full bg-green-400"></span>
                                Builder Agent
                            </button>
                        </div>

                        <form onSubmit={handleSubmit} className="relative">
                            <input
                                type="text"
                                value={inputMessage}
                                onChange={(e) => setInputMessage(e.target.value)}
                                placeholder={
                                    selectedAgent === 'all'
                                        ? "Ask the whole team..."
                                        : `Ask the ${selectedAgent.charAt(0).toUpperCase() + selectedAgent.slice(1)} Agent...`
                                }
                                className="w-full p-4 pr-12 bg-gray-100 dark:bg-gray-900 border-none rounded-xl focus:ring-2 focus:ring-purple-500 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                                disabled={loading}
                            />
                            <button
                                type="submit"
                                disabled={loading || !inputMessage.trim()}
                                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-purple-600 hover:bg-purple-100 dark:hover:bg-purple-900/30 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                </svg>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}
