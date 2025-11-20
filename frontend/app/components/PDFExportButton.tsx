'use client';

import React from 'react';
import { PDFDownloadLink } from '@react-pdf/renderer';
import SessionPDFDocument from './SessionPDFDocument';
import { ProjectPlan } from './ProjectPlanView';

interface Message {
    agent: string;
    content: string | ProjectPlan;
    timestamp: string;
}

interface PDFExportButtonProps {
    sessionTitle: string;
    messages: Message[];
    sessionId: string;
}

export function PDFExportButton({ sessionTitle, messages, sessionId }: PDFExportButtonProps) {
    const fileName = `${(sessionTitle || 'session').replace(/[^a-z0-9]/gi, '_').toLowerCase()}_${new Date().toISOString().split('T')[0]}.pdf`;

    return (
        <PDFDownloadLink
            document={
                <SessionPDFDocument
                    sessionTitle={sessionTitle}
                    messages={messages}
                    sessionId={sessionId}
                />
            }
            fileName={fileName}
        >
            {({ blob, url, loading, error }) => (
                <button
                    className="p-2 text-gray-500 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 rounded-lg hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-colors disabled:opacity-50"
                    title={loading ? 'Preparing PDF...' : 'Export to PDF'}
                    disabled={loading}
                >
                    {loading ? (
                        <svg className="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                    ) : (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    )}
                </button>
            )}
        </PDFDownloadLink>
    );
}
