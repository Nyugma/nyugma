/**
 * User Dashboard - Profile and Activity Management
 */

// Require authentication
if (!requireAuth()) {
    // Will redirect to login if not authenticated
}

document.addEventListener('DOMContentLoaded', async function() {
    const user = getCurrentUser();
    
    if (!user) {
        window.location.href = 'auth.html';
        return;
    }
    
    // Update welcome message
    document.getElementById('welcomeTitle').textContent = `Welcome, ${user.full_name}!`;
    document.getElementById('welcomeSubtitle').textContent = 
        user.user_type === 'helper' 
            ? 'Thank you for helping others with your experience' 
            : 'Find similar cases and connect with experienced helpers';
    
    // Load profile information
    loadProfileInfo(user);
    
    // Load quick actions based on user type
    loadQuickActions(user);
    
    // Load statistics
    loadStatistics(user);
    
    // Hide "Add Case" link if not a helper
    if (user.user_type !== 'helper') {
        const addCaseLink = document.getElementById('addCaseLink');
        if (addCaseLink) {
            addCaseLink.style.display = 'none';
        }
    }
});

/**
 * Load profile information
 */
function loadProfileInfo(user) {
    const profileInfo = document.getElementById('profileInfo');
    
    const userTypeLabel = user.user_type === 'helper' ? 'Helper' : 'New Litigant';
    const userTypeBadgeClass = user.user_type === 'helper' ? 'helper' : 'new-litigant';
    
    profileInfo.innerHTML = `
        <div class="profile-item">
            <span class="profile-label">Full Name</span>
            <span class="profile-value">${user.full_name}</span>
        </div>
        
        <div class="profile-item">
            <span class="profile-label">Email</span>
            <span class="profile-value">${user.email}</span>
        </div>
        
        <div class="profile-item">
            <span class="profile-label">User Type</span>
            <span class="profile-badge ${userTypeBadgeClass}">${userTypeLabel}</span>
        </div>
        
        ${user.phone ? `
        <div class="profile-item">
            <span class="profile-label">Phone</span>
            <span class="profile-value">${user.phone}</span>
        </div>
        ` : ''}
        
        ${user.city ? `
        <div class="profile-item">
            <span class="profile-label">City</span>
            <span class="profile-value">${user.city}</span>
        </div>
        ` : ''}
        
        ${user.state ? `
        <div class="profile-item">
            <span class="profile-label">State</span>
            <span class="profile-value">${user.state}</span>
        </div>
        ` : ''}
        
        <div class="profile-item">
            <span class="profile-label">Member Since</span>
            <span class="profile-value">${formatDate(user.created_at)}</span>
        </div>
        
        ${user.user_type === 'helper' ? `
        <div class="profile-item">
            <span class="profile-label">Reputation Score</span>
            <span class="profile-value">${user.reputation_score.toFixed(1)} / 5.0</span>
        </div>
        ` : ''}
    `;
}

/**
 * Load quick actions based on user type
 */
function loadQuickActions(user) {
    const quickActions = document.getElementById('quickActions');
    
    if (user.user_type === 'helper') {
        // Actions for helpers
        quickActions.innerHTML = `
            <a href="helper-dashboard.html" class="action-card">
                <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 5v14M5 12h14"></path>
                </svg>
                <div class="action-title">Add New Case</div>
                <div class="action-description">Share your past case experience</div>
            </a>
            
            <a href="connections.html" class="action-card">
                <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <div class="action-title">My Connections</div>
                <div class="action-description">View and manage connections</div>
            </a>
            
            <div class="action-card" onclick="alert('Coming soon!')">
                <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <div class="action-title">My Cases</div>
                <div class="action-description">View your submitted cases</div>
            </div>
        `;
    } else {
        // Actions for new litigants
        quickActions.innerHTML = `
            <a href="search.html" class="action-card">
                <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="m21 21-4.35-4.35"></path>
                </svg>
                <div class="action-title">Search Cases</div>
                <div class="action-description">Find similar legal cases</div>
            </a>
            
            <a href="connections.html" class="action-card">
                <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                    <circle cx="9" cy="7" r="4"></circle>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
                <div class="action-title">My Connections</div>
                <div class="action-description">View connection requests</div>
            </a>
            
            <a href="messages.html" class="action-card">
                <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <div class="action-title">Messages</div>
                <div class="action-description">Chat with helpers</div>
            </a>
            
            <div class="action-card" onclick="alert('Coming soon!')">
                <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                    <circle cx="9" cy="7" r="4"></circle>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
                <div class="action-title">Find Helpers</div>
                <div class="action-description">Connect with experienced litigants</div>
            </div>
            
            <a href="inquiry.html" class="action-card">
                <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <div class="action-title">Legal Inquiry</div>
                <div class="action-description">Schedule a consultation</div>
            </a>
        `;
    }
}

/**
 * Load user statistics
 */
function loadStatistics(user) {
    const statsGrid = document.getElementById('statsGrid');
    
    if (user.user_type === 'helper') {
        // Stats for helpers
        statsGrid.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${user.cases_helped || 0}</div>
                <div class="stat-label">People Helped</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">${user.total_ratings || 0}</div>
                <div class="stat-label">Total Ratings</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">${user.reputation_score ? user.reputation_score.toFixed(1) : '0.0'}</div>
                <div class="stat-label">Reputation</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">${calculateDaysSince(user.created_at)}</div>
                <div class="stat-label">Days Active</div>
            </div>
        `;
    } else {
        // Stats for new litigants
        statsGrid.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">0</div>
                <div class="stat-label">Cases Searched</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">0</div>
                <div class="stat-label">Connections Made</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">0</div>
                <div class="stat-label">Messages Sent</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">${calculateDaysSince(user.created_at)}</div>
                <div class="stat-label">Days Active</div>
            </div>
        `;
    }
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

/**
 * Calculate days since a date
 */
function calculateDaysSince(dateString) {
    if (!dateString) return 0;
    
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}
