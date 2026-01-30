/**
 * Frontend Configuration
 * Manages backend API URL for different environments
 */

const Config = {
    /**
     * Get backend URL based on current environment
     * @returns {string} Backend API base URL
     */
    getBackendUrl: function() {
        // Check if running in development (localhost)
        if (window.location.hostname === 'localhost' || 
            window.location.hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        }
        
        // Production: Use environment variable or default
        return window.ENV?.BACKEND_URL || 'https://your-api.onrender.com';
    },
    
    /**
     * API endpoint paths
     */
    endpoints: {
        upload: '/api/upload',
        health: '/api/health',
        cases: '/api/cases',
        performance: '/api/performance'
    },
    
    /**
     * Get full endpoint URL
     * @param {string} endpoint - Endpoint key from endpoints object
     * @returns {string} Full URL for the endpoint
     */
    getEndpoint: function(endpoint) {
        return this.getBackendUrl() + this.endpoints[endpoint];
    }
};

// Export for use in other modules
window.AppConfig = Config;
