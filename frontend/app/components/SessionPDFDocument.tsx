import React from 'react';
import { Document, Page, Text, View, StyleSheet, Font } from '@react-pdf/renderer';
import { ProjectPlan } from './ProjectPlanView';

interface Message {
    agent: string;
    content: string | ProjectPlan;
    timestamp: string;
}

interface SessionPDFDocumentProps {
    sessionTitle: string;
    messages: Message[];
    sessionId: string;
}

// Define styles for the PDF
const styles = StyleSheet.create({
    page: {
        padding: 40,
        backgroundColor: '#ffffff',
        fontFamily: 'Helvetica',
    },
    header: {
        marginBottom: 30,
        borderBottom: '2 solid #9333ea',
        paddingBottom: 15,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#9333ea',
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 10,
        color: '#6b7280',
        marginBottom: 4,
    },
    section: {
        marginBottom: 20,
    },
    agentHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 10,
        backgroundColor: '#f3f4f6',
        padding: 10,
        borderRadius: 4,
    },
    agentName: {
        fontSize: 12,
        fontWeight: 'bold',
        color: '#374151',
    },
    timestamp: {
        fontSize: 9,
        color: '#9ca3af',
        marginLeft: 8,
    },
    content: {
        fontSize: 10,
        lineHeight: 1.5,
        color: '#1f2937',
        marginBottom: 15,
    },
    storyCard: {
        marginBottom: 15,
        padding: 12,
        backgroundColor: '#f9fafb',
        borderLeft: '3 solid #9333ea',
        borderRadius: 4,
    },
    storyTitle: {
        fontSize: 11,
        fontWeight: 'bold',
        color: '#1f2937',
        marginBottom: 6,
    },
    priorityBadge: {
        fontSize: 8,
        color: '#ffffff',
        padding: '4 8',
        borderRadius: 3,
        marginBottom: 8,
        alignSelf: 'flex-start',
    },
    priorityHigh: {
        backgroundColor: '#dc2626',
    },
    priorityMedium: {
        backgroundColor: '#f59e0b',
    },
    priorityLow: {
        backgroundColor: '#10b981',
    },
    gherkinBlock: {
        backgroundColor: '#f3f4f6',
        padding: 8,
        marginVertical: 6,
        borderRadius: 3,
        fontFamily: 'Courier',
    },
    gherkinText: {
        fontSize: 9,
        color: '#374151',
        lineHeight: 1.4,
    },
    taskList: {
        marginTop: 8,
    },
    taskItem: {
        fontSize: 9,
        color: '#4b5563',
        marginBottom: 4,
        paddingLeft: 12,
    },
    sectionTitle: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#9333ea',
        marginTop: 20,
        marginBottom: 12,
        borderBottom: '1 solid #e5e7eb',
        paddingBottom: 6,
    },
    footer: {
        position: 'absolute',
        bottom: 30,
        left: 40,
        right: 40,
        textAlign: 'center',
        fontSize: 8,
        color: '#9ca3af',
        borderTop: '1 solid #e5e7eb',
        paddingTop: 10,
    },
});

const SessionPDFDocument: React.FC<SessionPDFDocumentProps> = ({ sessionTitle, messages, sessionId }) => {
    const formatTimestamp = (timestamp: string) => {
        const date = new Date(timestamp);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const getAgentName = (agent: string) => {
        switch (agent) {
            case 'idea': return 'Idea Agent';
            case 'critic': return 'Critic Agent';
            case 'builder': return 'Builder Agent';
            case 'user': return 'User Prompt';
            default: return 'System';
        }
    };

    const renderProjectPlan = (plan: ProjectPlan) => (
        <>
            {/* User Stories Section */}
            {plan.stories && plan.stories.length > 0 && (
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>User Stories</Text>
                    {plan.stories.map((story, idx) => (
                        <View key={idx} style={styles.storyCard}>
                            <View style={[
                                styles.priorityBadge,
                                story.priority === 'High' ? styles.priorityHigh :
                                    story.priority === 'Medium' ? styles.priorityMedium :
                                        styles.priorityLow
                            ]}>
                                <Text>{story.priority} Priority</Text>
                            </View>
                            <Text style={styles.storyTitle}>{story.title}</Text>
                            <View style={styles.gherkinBlock}>
                                <Text style={styles.gherkinText}>{story.gherkin}</Text>
                            </View>
                        </View>
                    ))}
                </View>
            )}

            {/* Technical Tasks Section */}
            {plan.tasks && plan.tasks.length > 0 && (
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Technical Tasks</Text>
                    <View style={styles.taskList}>
                        {plan.tasks.map((task, idx) => (
                            <Text key={idx} style={styles.taskItem}>
                                • {task}
                            </Text>
                        ))}
                    </View>
                </View>
            )}
        </>
    );

    return (
        <Document>
            <Page size="A4" style={styles.page}>
                {/* Header */}
                <View style={styles.header}>
                    <Text style={styles.title}>{sessionTitle || 'Brainstorming Session'}</Text>
                    <Text style={styles.subtitle}>Session ID: {sessionId.slice(0, 12)}...</Text>
                    <Text style={styles.subtitle}>Generated: {new Date().toLocaleString()}</Text>
                </View>

                {/* Messages */}
                {messages.map((msg, idx) => {
                    if (msg.agent === 'builder' && typeof msg.content === 'object') {
                        // Render project plan
                        return (
                            <View key={idx} style={styles.section}>
                                <View style={styles.agentHeader}>
                                    <Text style={styles.agentName}>{getAgentName(msg.agent)}</Text>
                                    <Text style={styles.timestamp}>{formatTimestamp(msg.timestamp)}</Text>
                                </View>
                                {renderProjectPlan(msg.content as ProjectPlan)}
                            </View>
                        );
                    } else if (msg.agent === 'builder' && typeof msg.content === 'string') {
                        // Try to parse JSON
                        try {
                            if (msg.content.trim().startsWith('{')) {
                                const parsed = JSON.parse(msg.content);
                                if (parsed.stories && parsed.tasks) {
                                    return (
                                        <View key={idx} style={styles.section}>
                                            <View style={styles.agentHeader}>
                                                <Text style={styles.agentName}>{getAgentName(msg.agent)}</Text>
                                                <Text style={styles.timestamp}>{formatTimestamp(msg.timestamp)}</Text>
                                            </View>
                                            {renderProjectPlan(parsed)}
                                        </View>
                                    );
                                }
                            }
                        } catch (e) {
                            // Fall through to text rendering
                        }
                    }

                    // Regular text content
                    return (
                        <View key={idx} style={styles.section}>
                            <View style={styles.agentHeader}>
                                <Text style={styles.agentName}>{getAgentName(msg.agent)}</Text>
                                <Text style={styles.timestamp}>{formatTimestamp(msg.timestamp)}</Text>
                            </View>
                            <Text style={styles.content}>
                                {typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content, null, 2)}
                            </Text>
                        </View>
                    );
                })}

                {/* Footer */}
                <Text style={styles.footer} fixed>
                    Generated by TeamSpark AI - Multi-Agent Brainstorming System
                </Text>
            </Page>
        </Document>
    );
};

export default SessionPDFDocument;
