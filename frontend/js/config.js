// Configuration for different environments
const config = {
    // Check if we're in development or production
    isDevelopment: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1',
    
    // API base URL - will be set dynamically
    get apiBaseUrl() {
        if (this.isDevelopment) {
            return 'http://localhost:8000/api';
        } else {
            // Production URL - will be your Vercel domain
            return `${window.location.origin}/api`;
        }
    }
};

// Make config available globally
window.APP_CONFIG = config;
