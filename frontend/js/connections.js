/**
 * Connections Management
 * Handle connection requests and accepted connections
 */

// Require authentication
if (!requireAuth()) {
    // Will redirect to login if not authenticated
}

class ConnectionsManager {
    constructor() {
        this.apiBaseUrl = window.AppConfig.getBackendUrl();
        this.currentUser = getCurrentUser();
        this.currentTab = 'pending';
        
        this.initializeElements();
        this.bindEvents();
        this.loadConnections();
    }

    initializeElements() {
        // Tab buttons
        this.tabButtons = document.querySelectorAll('.tab-button');
        this.tabContents = document.querySelectorAll('.tab-content');
        
        // Pending tab elements
        this.pendingLoading = document.getElementById('pendingLoading');
        this.pendingEmpty = document.getElementById('pendingEmpty');
        this.pendingConnections = document.getElementById('pendingConnections');
        this.pendingBadge = document.getElementById('pendingBadge');
        
        // Accepted tab elements
        this.acceptedLoading = document.getElementById('acceptedLoading');
        this.acceptedEmpty = document.getElementById('acceptedEmpty');
        this.acceptedConnections = document.getElementById('acceptedConnections');
        this.acceptedBadge = document.getElementById('acceptedBadge');
        
        // Update subtitle based on user type
        const subtitle = document.getElementById('pageSubtitle');
        const emptyMessage = document.getElementById('pendingEmptyMessage');
        
        if (this.currentUser.user_type === 'helper') {
            subtitle.textContent = 'Review connection requests from seekers and manage your connections';
            emptyMessage.textContent = 'No one has requested to connect with you yet.';
        } else {
            subtitle.textContent = 'View your connection requests and accepted connections';
            emptyMessage.textContent = 'You haven\'t sent any connection requests yet.';
        }
    }

    bindEvents() {
        // Tab switching
        this.tabButtons.forEach(button => {
            button.addEventListener('click', () => this.switchTab(button.dataset.tab));
        });
    }

    switchTab(tabName) {
        this.currentTab = tabName;
        
        // Update tab buttons
        this.tabButtons.forEach(btn => {
            if (btn.dataset.tab === tabName) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // Update tab contents
        this.tabContents.forEach(content => {
            if (content.id === `${tabName}-tab`) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
    }

    async loadConnections() {
        await Promise.all([
            this.loadPendingConnections(),
            this.loadAcceptedConnections()
        ]);
    }

    async loadPendingConnections() {
        try {
            this.pendingLoading.style.display = 'block';
            this.pendingEmpty.style.display = 'none';
            this.pendingConnections.innerHTML = '';
            
            const response = await authenticatedFetch(`${this.apiBaseUrl}/api/connections/pending`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to load pending connections');
            }
            
            this.pendingLoading.style.display = 'none';
            
            if (data.connections.length === 0) {
                this.pendingEmpty.style.display = 'block';
                this.pendingBadge.textContent = '0';
            } else {
                this.pendingBadge.textContent = data.connections.length;
                data.connections.forEach(conn => {
                    const card = this.createConnectionCard(conn, 'pending');
                    this.pendingConnections.appendChild(card);
                });
            }
            
        } catch (error) {
            console.error('Error loading pending connections:', error);
            this.pendingLoading.style.display = 'none';
            this.pendingEmpty.style.display = 'block';
            this.pendingEmpty.innerHTML = `
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="15" y1="9" x2="9" y2="15"></line>
                    <line x1="9" y1="9" x2="15" y2="15"></line>
                </svg>
                <h3>Error Loading Connections</h3>
                <p>${error.message}</p>
            `;
        }
    }

    async loadAcceptedConnections() {
        try {
            this.acceptedLoading.style.display = 'block';
            this.acceptedEmpty.style.display = 'none';
            this.acceptedConnections.innerHTML = '';
            
            const response = await authenticatedFetch(`${this.apiBaseUrl}/api/connections/accepted`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to load accepted connections');
            }
            
            this.acceptedLoading.style.display = 'none';
            
            if (data.connections.length === 0) {
                this.acceptedEmpty.style.display = 'block';
                this.acceptedBadge.textContent = '0';
            } else {
                this.acceptedBadge.textContent = data.connections.length;
                data.connections.forEach(conn => {
                    const card = this.createConnectionCard(conn, 'accepted');
                    this.acceptedConnections.appendChild(card);
                });
            }
            
        } catch (error) {
            console.error('Error loading accepted connections:', error);
            this.acceptedLoading.style.display = 'none';
            this.acceptedEmpty.style.display = 'block';
            this.acceptedEmpty.innerHTML = `
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="15" y1="9" x2="9" y2="15"></line>
                    <line x1="9" y1="9" x2="15" y2="15"></line>
                </svg>
                <h3>Error Loading Connections</h3>
                <p>${error.message}</p>
            `;
        }
    }

    createConnectionCard(connection, type) {
        const card = document.createElement('div');
        card.className = 'connection-card';
        
        // Determine which user info to show
        let otherUser;
        let userRole;
        
        if (type === 'pending') {
            if (this.currentUser.user_type === 'helper') {
                otherUser = connection.requester_info;
                userRole = 'Seeker';
            } else {
                otherUser = connection.helper_info;
                userRole = 'Helper';
            }
        } else {
            otherUser = connection.other_user;
            userRole = connection.other_user?.user_type === 'helper' ? 'Helper' : 'Seeker';
        }
        
        if (!otherUser) {
            otherUser = { full_name: 'Unknown User', email: 'N/A' };
        }
        
        const createdDate = new Date(connection.created_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        card.innerHTML = `
            <div class="connection-header">
                <div class="connection-user-info">
                    <h3>${this.escapeHtml(otherUser.full_name)}</h3>
                    <span class="user-type-badge ${userRole.toLowerCase()}">${userRole}</span>
                </div>
                ${type === 'pending' && this.currentUser.user_type === 'helper' ? `
                    <span class="status-badge pending">Pending</span>
                ` : type === 'accepted' ? `
                    <span class="status-badge accepted">Connected</span>
                ` : `
                    <span class="status-badge pending">Waiting</span>
                `}
            </div>
            
            <div class="connection-details">
                ${otherUser.city && otherUser.state ? `
                    <div class="detail-item">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                            <circle cx="12" cy="10" r="3"></circle>
                        </svg>
                        <span>${this.escapeHtml(otherUser.city)}, ${this.escapeHtml(otherUser.state)}</span>
                    </div>
                ` : ''}
                
                <div class="detail-item">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="16" y1="2" x2="16" y2="6"></line>
                        <line x1="8" y1="2" x2="8" y2="6"></line>
                        <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                    <span>Requested on ${createdDate}</span>
                </div>
                
                ${otherUser.reputation_score !== undefined && otherUser.reputation_score !== null ? `
                    <div class="detail-item">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"></polygon>
                        </svg>
                        <span>Reputation: ${otherUser.reputation_score.toFixed(1)}/5.0</span>
                    </div>
                ` : ''}
                
                ${connection.message ? `
                    <div class="connection-message">
                        <strong>Message:</strong>
                        <p>${this.escapeHtml(connection.message)}</p>
                    </div>
                ` : ''}
            </div>
            
            <div class="connection-actions">
                ${type === 'pending' && this.currentUser.user_type === 'helper' ? `
                    <button class="btn btn-primary" onclick="connectionsManager.acceptConnection('${connection.connection_id}')">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                        Accept
                    </button>
                    <button class="btn btn-secondary" onclick="connectionsManager.declineConnection('${connection.connection_id}')">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                        Decline
                    </button>
                ` : type === 'pending' ? `
                    <button class="btn btn-secondary" onclick="connectionsManager.cancelConnection('${connection.connection_id}')">
                        Cancel Request
                    </button>
                ` : `
                    <a href="messages.html?connection_id=${connection.connection_id}" class="btn btn-primary">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        </svg>
                        Message
                    </a>
                    <button class="btn btn-secondary" onclick="connectionsManager.showRatingModal('${connection.connection_id}', '${otherUser.user_id}', '${this.escapeHtml(otherUser.full_name)}')">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"></polygon>
                        </svg>
                        Rate
                    </button>
                `}
            </div>
        `;
        
        return card;
    }

    async acceptConnection(connectionId) {
        if (!confirm('Accept this connection request?')) {
            return;
        }
        
        try {
            const response = await authenticatedFetch(
                `${this.apiBaseUrl}/api/connections/${connectionId}/accept`,
                { method: 'PATCH' }
            );
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to accept connection');
            }
            
            alert('Connection accepted! You can now message this user.');
            this.loadConnections();
            
        } catch (error) {
            console.error('Error accepting connection:', error);
            alert('Failed to accept connection. Please try again.');
        }
    }

    async declineConnection(connectionId) {
        if (!confirm('Decline this connection request?')) {
            return;
        }
        
        try {
            const response = await authenticatedFetch(
                `${this.apiBaseUrl}/api/connections/${connectionId}/decline`,
                { method: 'PATCH' }
            );
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to decline connection');
            }
            
            alert('Connection request declined.');
            this.loadConnections();
            
        } catch (error) {
            console.error('Error declining connection:', error);
            alert('Failed to decline connection. Please try again.');
        }
    }

    async cancelConnection(connectionId) {
        if (!confirm('Cancel this connection request?')) {
            return;
        }
        
        try {
            const response = await authenticatedFetch(
                `${this.apiBaseUrl}/api/connections/${connectionId}`,
                { method: 'DELETE' }
            );
            
            if (!response.ok && response.status !== 204) {
                const data = await response.json();
                throw new Error(data.message || 'Failed to cancel connection');
            }
            
            alert('Connection request cancelled.');
            this.loadConnections();
            
        } catch (error) {
            console.error('Error cancelling connection:', error);
            alert('Failed to cancel connection. Please try again.');
        }
    }

    async removeConnection(connectionId) {
        if (!confirm('Remove this connection? You can always reconnect later.')) {
            return;
        }
        
        try {
            const response = await authenticatedFetch(
                `${this.apiBaseUrl}/api/connections/${connectionId}`,
                { method: 'DELETE' }
            );
            
            if (!response.ok && response.status !== 204) {
                const data = await response.json();
                throw new Error(data.message || 'Failed to remove connection');
            }
            
            alert('Connection removed.');
            this.loadConnections();
            
        } catch (error) {
            console.error('Error removing connection:', error);
            alert('Failed to remove connection. Please try again.');
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Rating Modal Methods
    showRatingModal(connectionId, ratedUserId, userName) {
        this.currentRatingConnection = connectionId;
        this.currentRatedUser = ratedUserId;
        this.selectedRating = 0;
        
        document.getElementById('ratingUserName').textContent = userName;
        document.getElementById('reviewText').value = '';
        document.getElementById('ratingText').textContent = 'Click to rate';
        document.getElementById('submitRatingBtn').disabled = true;
        
        // Reset stars
        document.querySelectorAll('.star').forEach(star => {
            star.classList.remove('selected');
        });
        
        // Add star click handlers
        document.querySelectorAll('.star').forEach(star => {
            star.onclick = () => this.selectRating(parseInt(star.dataset.rating));
        });
        
        document.getElementById('ratingModal').style.display = 'flex';
    }

    selectRating(rating) {
        this.selectedRating = rating;
        
        // Update stars
        document.querySelectorAll('.star').forEach(star => {
            const starRating = parseInt(star.dataset.rating);
            if (starRating <= rating) {
                star.classList.add('selected');
            } else {
                star.classList.remove('selected');
            }
        });
        
        // Update text
        const ratingTexts = {
            1: 'Poor',
            2: 'Fair',
            3: 'Good',
            4: 'Very Good',
            5: 'Excellent'
        };
        document.getElementById('ratingText').textContent = ratingTexts[rating];
        document.getElementById('submitRatingBtn').disabled = false;
    }

    closeRatingModal() {
        document.getElementById('ratingModal').style.display = 'none';
        this.currentRatingConnection = null;
        this.currentRatedUser = null;
        this.selectedRating = 0;
    }

    async submitRating() {
        if (!this.selectedRating || !this.currentRatingConnection || !this.currentRatedUser) {
            alert('Please select a rating');
            return;
        }
        
        const review = document.getElementById('reviewText').value.trim();
        
        try {
            document.getElementById('submitRatingBtn').disabled = true;
            
            const response = await authenticatedFetch(
                `${this.apiBaseUrl}/api/ratings`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        connection_id: this.currentRatingConnection,
                        rated_user_id: this.currentRatedUser,
                        rating: this.selectedRating,
                        review: review || null
                    })
                }
            );
            
            const data = await response.json();
            
            if (!response.ok) {
                if (response.status === 409) {
                    alert('You have already rated this user for this connection.');
                } else {
                    throw new Error(data.message || 'Failed to submit rating');
                }
                return;
            }
            
            alert('Rating submitted successfully! Thank you for your feedback.');
            this.closeRatingModal();
            this.loadConnections();
            
        } catch (error) {
            console.error('Error submitting rating:', error);
            alert('Failed to submit rating. Please try again.');
        } finally {
            document.getElementById('submitRatingBtn').disabled = false;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.connectionsManager = new ConnectionsManager();
});
