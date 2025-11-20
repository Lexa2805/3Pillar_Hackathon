'use client';

import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import toast from 'react-hot-toast';

interface MermaidProps {
    chart: string;
}

export function Mermaid({ chart }: MermaidProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const renderIdRef = useRef(0);
    const [isRendered, setIsRendered] = useState(false);

    useEffect(() => {
        if (!containerRef.current || !chart) return;

        // Initialize mermaid with theme support
        mermaid.initialize({
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'loose',
            fontFamily: 'system-ui, -apple-system, sans-serif',
        });

        const renderChart = async () => {
            if (!containerRef.current) return;

            try {
                renderIdRef.current += 1;
                const uniqueId = `mermaid-${Date.now()}-${renderIdRef.current}`;
                
                // Clear previous content
                containerRef.current.innerHTML = '';

                // Render the chart
                const { svg } = await mermaid.render(uniqueId, chart);
                containerRef.current.innerHTML = svg;
                setIsRendered(true);
            } catch (error) {
                console.error('Mermaid rendering error:', error);
                containerRef.current.innerHTML = `
                    <div class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                        <p class="text-red-600 dark:text-red-400 text-sm font-medium">Failed to render diagram</p>
                        <pre class="mt-2 text-xs text-red-500 dark:text-red-300 overflow-x-auto">${error}</pre>
                    </div>
                `;
                setIsRendered(false);
            }
        };

        renderChart();
    }, [chart]);

    const handleDownload = async () => {
        if (!containerRef.current || !isRendered) return;

        try {
            const svgElement = containerRef.current.querySelector('svg');
            if (!svgElement) {
                toast.error('No diagram to download');
                return;
            }

            // Clone the SVG to avoid modifying the displayed one
            const clonedSvg = svgElement.cloneNode(true) as SVGElement;
            
            // Get SVG dimensions
            const bbox = svgElement.getBBox();
            const width = bbox.width + 40;
            const height = bbox.height + 40;
            
            clonedSvg.setAttribute('width', width.toString());
            clonedSvg.setAttribute('height', height.toString());
            
            // Add white background as a rect element
            const backgroundRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            backgroundRect.setAttribute('width', '100%');
            backgroundRect.setAttribute('height', '100%');
            backgroundRect.setAttribute('fill', 'white');
            clonedSvg.insertBefore(backgroundRect, clonedSvg.firstChild);

            // Convert SVG to string
            const svgData = new XMLSerializer().serializeToString(clonedSvg);
            
            // Add XML declaration and encoding
            const svgWithDeclaration = '<?xml version="1.0" encoding="UTF-8"?>\n' + svgData;
            
            // Create blob and download as SVG (better quality than PNG)
            const svgBlob = new Blob([svgWithDeclaration], { type: 'image/svg+xml;charset=utf-8' });
            const url = URL.createObjectURL(svgBlob);
            
            const link = document.createElement('a');
            link.download = 'architecture-diagram.svg';
            link.href = url;
            link.click();
            
            URL.revokeObjectURL(url);
            toast.success('Diagram downloaded as SVG!');
        } catch (error) {
            console.error('Download error:', error);
            toast.error('Failed to download diagram');
        }
    };

    return (
        <div className="relative">
            {isRendered && (
                <button
                    onClick={handleDownload}
                    className="absolute top-2 right-2 z-10 p-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg shadow-lg transition-colors flex items-center gap-2 text-sm font-medium"
                    title="Download diagram as PNG"
                >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    <span className="hidden sm:inline">Download</span>
                </button>
            )}
            <div 
                ref={containerRef} 
                className="mermaid-container flex justify-center items-center p-4 bg-white dark:bg-gray-900 rounded-xl overflow-x-auto"
            />
        </div>
    );
}
