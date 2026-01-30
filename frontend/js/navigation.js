/**
 * Navigation and API Documentation Link Handler
 * Manages navigation highlighting and dynamic API documentation links
 */

document.addEventListener('DOMContentLoaded', () => {
    // Update API documentation links with backend URL
    const apiDocsLink = document.getElementById('apiDocsLink');
    const apiDocsButton = document.getElementById('apiDocsButton');
    
    if (window.AppConfig) {
        const backendUrl = window.AppConfig.getBackendUrl();
        const docsUrl = `${backendUrl}/docs`;
        
        // Update navigation API docs link
        if (apiDocsLink) {
            apiDocsLink.href = docsUrl;
            apiDocsLink.setAttribute('target', '_blank');
            apiDocsLink.setAttribute('rel', 'noopener noreferrer');
        }
        
        // Update home page API docs button
        if (apiDocsButton) {
            apiDocsButton.href = docsUrl;
        }
    }
    
    // Handle navigation highlighting for current page
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-link').forEach(link => {
        const linkHref = link.getAttribute('href');
        if (linkHref && linkHref.includes(currentPage)) {
            link.classList.add('active');
        } else if (linkHref && !linkHref.includes('#')) {
            link.classList.remove('active');
        }
    });
});
