'use client';

import { ThemeProvider } from 'next-themes';
import { Toaster } from 'react-hot-toast';

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange={false}
        >
            {children}
            <Toaster
                position="top-right"
                reverseOrder={false}
                gutter={8}
                toastOptions={{
                    // Default options
                    duration: 4000,
                    className: '',
                    style: {
                        background: 'var(--background)',
                        color: 'var(--foreground)',
                        border: '1px solid rgb(229 231 235)',
                    },
                    // Success
                    success: {
                        duration: 3000,
                        style: {
                            background: 'var(--background)',
                            color: 'var(--foreground)',
                            border: '1px solid rgb(34 197 94)',
                        },
                        iconTheme: {
                            primary: '#10b981',
                            secondary: 'var(--background)',
                        },
                    },
                    // Error
                    error: {
                        duration: 4000,
                        style: {
                            background: 'var(--background)',
                            color: 'var(--foreground)',
                            border: '1px solid rgb(239 68 68)',
                        },
                        iconTheme: {
                            primary: '#ef4444',
                            secondary: 'var(--background)',
                        },
                    },
                }}
            />
        </ThemeProvider>
    );
}
