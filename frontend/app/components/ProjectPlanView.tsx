import React from 'react';
import { motion } from 'framer-motion';

export interface UserStory {
    title: string;
    gherkin: string;
    priority: string;
}

export interface ProjectPlan {
    stories: UserStory[];
    tasks: string[];
    mermaid_code?: string;
}

export function ProjectPlanView({ plan }: { plan: ProjectPlan }) {
    if (!plan || !plan.stories) return null;

    return (
        <div className="space-y-8 w-full">
            <div>
                <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                    <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400">
                        📋
                    </span>
                    User Stories
                </h3>
                <div className="grid gap-4 grid-cols-1 lg:grid-cols-2">
                    {plan.stories.map((story, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            className="bg-white dark:bg-gray-800/50 p-5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-all hover:border-purple-500/30 group"
                        >
                            <div className="flex justify-between items-start mb-3">
                                <h4 className="font-semibold text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                                    {story.title}
                                </h4>
                                <span className={`text-xs px-2.5 py-1 rounded-full font-medium border ${story.priority === 'High'
                                        ? 'bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800'
                                        : story.priority === 'Medium'
                                            ? 'bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400 dark:border-yellow-800'
                                            : 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800'
                                    }`}>
                                    {story.priority}
                                </span>
                            </div>
                            <div className="bg-gray-50 dark:bg-gray-900/50 p-3 rounded-lg text-sm font-mono text-gray-600 dark:text-gray-400 whitespace-pre-wrap border border-gray-100 dark:border-gray-800">
                                {story.gherkin}
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>

            <div>
                <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                    <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400">
                        ✅
                    </span>
                    Technical Tasks
                </h3>
                <div className="bg-white dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
                    {plan.tasks.map((task, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.2 + (idx * 0.05) }}
                            className="flex items-start gap-3 p-4 border-b border-gray-100 dark:border-gray-700/50 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors group"
                        >
                            <div className="mt-1 w-5 h-5 rounded border-2 border-gray-300 dark:border-gray-600 flex-shrink-0 group-hover:border-blue-500 transition-colors" />
                            <span className="text-gray-700 dark:text-gray-300 leading-relaxed">{task}</span>
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    );
}
