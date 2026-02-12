/**
 * Authentication utility functions
 * Shared across all pages that need authentication
 */

/**
 * Get backend URL (wrapper for Config)
 */
function getBackendUrl() {
    if (window.AppConfig) {
        return window.AppConfig.getBackendUrl();
    }
    // Fallback for development
    return 'http://localhost:8000';
}

/**
 * Get current user from localStorage
 */
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

/**
 * Get access token from localStorage
 */
function getAccessToken() {
    return localStorage.getItem('access_token');
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return !!getAccessToken();
}

/**
 * Logout user
 */
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = 'auth.html';
}

/**
 * Require authentication - redirect to login if not authenticated
 */
function requireAuth() {
    if (!isAuthenticated()) {
        // Store current page to redirect back after login
        localStorage.setItem('redirect_after_login', window.location.pathname);
        window.location.href = 'auth.html';
        return false;
    }
    return true;
}

/**
 * Require specific user type
 */
function requireUserType(requiredType) {
    if (!requireAuth()) {
        return false;
    }
    
    const user = getCurrentUser();
    if (user.user_type !== requiredType) {
        alert(`This page is only accessible to ${requiredType === 'helper' ? 'helpers' : 'new litigants'}`);
        window.location.href = 'index.html';
        return false;
    }
    
    return true;
}

/**
 * Make authenticated API request
 */
async function authenticatedFetch(url, options = {}) {
    const token = getAccessToken();
    
    if (!token) {
        throw new Error('Not authenticated');
    }
    
    // Add authorization header
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    // Handle 401 Unauthorized - token expired or invalid
    if (response.status === 401) {
        logout();
        throw new Error('Session expired. Please login again.');
    }
    
    return response;
}

/**
 * Update navigation with user info
 */
function updateNavigation() {
    const user = getCurrentUser();
    const navLinks = document.querySelector('.nav-links');
    
    if (!navLinks) return;
    
    if (user) {
        // User is logged in - show user menu
        const userMenu = document.createElement('div');
        userMenu.className = 'user-menu';
        userMenu.innerHTML = `
            <div class="user-info">
                <span class="user-name">${user.full_name}</span>
                <span class="user-type">${user.user_type === 'helper' ? 'Helper' : 'New Litigant'}</span>
            </div>
            <button onclick="logout()" class="logout-btn">Logout</button>
        `;
        
        // Remove existing user menu if any
        const existingMenu = document.querySelector('.user-menu');
        if (existingMenu) {
            existingMenu.remove();
        }
        
        navLinks.appendChild(userMenu);
    } else {
        // User not logged in - show login link
        const loginLink = document.createElement('a');
        loginLink.href = 'auth.html';
        loginLink.className = 'nav-link';
        loginLink.textContent = 'Login';
        
        // Remove existing login link if any
        const existingLogin = navLinks.querySelector('a[href="auth.html"]');
        if (!existingLogin) {
            navLinks.appendChild(loginLink);
        }
    }
}

/**
 * Initialize auth on page load
 */
function initAuth() {
    updateNavigation();
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAuth);
} else {
    initAuth();
}
