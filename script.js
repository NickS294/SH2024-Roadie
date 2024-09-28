mermaid.initialize({
    startOnLoad: true,
    theme: 'base',
    themeVariables: {
        primaryColor: '#f5f5f7',
        primaryTextColor: '#1d1d1f',
        primaryBorderColor: '#a1a1a6',
        lineColor: '#a1a1a6',
        secondaryColor: '#ffffff',
        tertiaryColor: '#f5f5f7'
    }
});

// Wait for Mermaid to render, then make the roadmap visible
document.addEventListener('DOMContentLoaded', () => {
    mermaid.init(undefined, document.querySelectorAll('.mermaid'));
    const roadmap = document.querySelector('.mermaid');
    roadmap.style.visibility = 'visible';

    // Initial fit to width
    const containerWidth = document.querySelector('.roadmap-container').offsetWidth;
    const roadmapWidth = roadmap.offsetWidth;
    const initialZoomFactor = containerWidth / roadmapWidth; // Calculate initial zoom factor

    roadmap.style.transform = `scale(${initialZoomFactor})`; // Set initial zoom
    roadmap.style.transformOrigin = '0 0'; // Set transform origin to top left

    // Set scroll to center the content
    const offsetX = (roadmapWidth * initialZoomFactor - containerWidth) / 2; // Calculate the offset for centering
    document.querySelector('.roadmap-container').scrollLeft = offsetX;
});

// Pan functionality
const roadmapContainer = document.querySelector('.roadmap-container');
const roadmap = document.querySelector('.mermaid');
let isPanning = false;
let startX, startY, initialScrollLeft, initialScrollTop;

roadmapContainer.addEventListener('mousedown', (e) => {
    isPanning = true;
    startX = e.clientX;
    startY = e.clientY;
    initialScrollLeft = roadmapContainer.scrollLeft;
    initialScrollTop = roadmapContainer.scrollTop;

    roadmapContainer.style.cursor = 'grabbing'; // Change cursor style
});

document.addEventListener('mousemove', (e) => {
    if (isPanning) {
        const deltaX = e.clientX - startX;
        const deltaY = e.clientY - startY;
        roadmapContainer.scrollLeft = initialScrollLeft - deltaX;
        roadmapContainer.scrollTop = initialScrollTop - deltaY;
    }
});

document.addEventListener('mouseup', () => {
    if (isPanning) {
        isPanning = false;
        roadmapContainer.style.cursor = 'grab'; // Reset cursor style
    }
});

// Zoom functionality
let zoomFactor = initialZoomFactor; // Start with initial zoom factor

roadmapContainer.addEventListener('wheel', (e) => {
    e.preventDefault(); // Prevent default scroll behavior
    zoomFactor += e.deltaY * -0.001; // Adjust zoom factor based on scroll direction
    zoomFactor = Math.min(Math.max(0.5, zoomFactor), 3); // Limit zoom between 0.5 and 3

    roadmap.style.transform = `scale(${zoomFactor})`; // Apply scaling

    // Adjust scroll position to maintain centering
    const offsetX = (roadmap.offsetWidth * zoomFactor - roadmapContainer.offsetWidth) / 2;
    roadmapContainer.scrollLeft = offsetX;
});
