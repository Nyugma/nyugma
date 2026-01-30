/**
 * Admin Panel for Inquiry Management
 * Handles viewing and managing legal inquiries
 */

class AdminPanel {
    constructor() {
        // Validate configuration
        try {
            if (!window.AppConfig) {
                throw new Error('Configuration module not loaded');
            }
            
            this.apiBaseUrl = window.AppConfig.getBackendUrl();
            
            if (!this.apiBaseUrl) {
                throw new Error('Backend URL not configured');
            }
            
            console.log('Backend API URL:', this.apiBaseUrl);
        } catch (error) {
            console.error('Configuration error:', error);
            alert('Application configuration error. Please contact the administrator.');
            throw error;
        }

        this.initializeElements();
        this.bindEvents();
        this.loadData();
    }

    /**
     * Initialize DOM element references
     */
    initializeElements() {
        // Statistics elements
        this.statPending = document.getElementById('statPending');
        this.statReviewed = document.getElementById('statReviewed');
        this.statContacted = document.getElementById('statContacted');
        this.statTotal = document.getElementById('statTotal');
        
        // Filter elements
        this.statusFilter = document.getElementById('statusFilter');
        this.refreshButton = document.getElementById('refreshButton');
        
        // Content elements
        this.inquiriesContainer = document.getElementById('inquiriesContainer');
        this.loadingState = document.getElementById('loadingState');
        this.emptyState = document.getElementById('emptyState');
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        this.statusFilter.addEventListener('change', () => this.loadInquiries());
        this.refreshButton.addEventListener('click', () => this.loadData());
    }

    /**
     * Load all data (statistics and inquiries)
     */
    async loadData() {
        await Promise.all([
            this.loadStatistics(),
            this.loadInquiries()
        ]);
    }

    /**
     * Load inquiry statistics
     */
    async loadStatistics() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/inquiries/stats/summary`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const stats = await response.json();
            
            // Update statistics display
            this.statPending.textContent = stats.by_status?.pending || 0;
            this.statReviewed.textContent = stats.by_status?.reviewed || 0;
            this.statContacted.textContent = stats.by_status?.contacted || 0;
            this.statTotal.textContent = stats.total_inquiries || 0;
            
        } catch (error) {
            console.error('Error loading statistics:', error);
            // Don't show error to user, just log it
        }
    }

    /**
     * Load inquiries with optional status filter
     */
    async loadInquiries() {
        try {
            this.showLoading();
            
            const status = this.statusFilter.value;
            const url = status 
                ? `${this.apiBaseUrl}/api/inquiries?status=${status}`
                : `${this.apiBaseUrl}/api/inquiries`;
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            this.hideLoading();
            this.displayInquiries(data.inquiries);
            
        } catch (error) {
            console.error('Error loading inquiries:', error);
            this.hideLoading();
            this.showError('Failed to load inquiries. Please try again.');
        }
    }

    /**
     * Display inquiries in the container
     */
    displayInquiries(inquiries) {
        this.inquiriesContainer.innerHTML = '';
        
        if (!inquiries || inquiries.length === 0) {
            this.showEmpty();
            return;
        }
        
        this.hideEmpty();
        
        inquiries.forEach(inquiry => {
            const inquiryCard = this.createInquiryCard(inquiry);
            this.inquiriesContainer.appendChild(inquiryCard);
        });
    }

    /**
     * Create inquiry card element
     */
    createInquiryCard(inquiry) {
        const card = document.createElement('div');
        card.className = 'inquiry-card';
        
        const urgencyLabels = {
            'low': 'Low Priority',
            'medium': 'Medium Priority',
            'high': 'High Priority',
            'urgent': 'Urgent'
        };
        
        const caseTypeLabels = {
            'civil': 'Civil Case',
            'criminal': 'Criminal Case',
            'family': 'Family Law',
            'property': 'Property Dispute',
            'corporate': 'Corporate/Business Law',
            'labor': 'Labor/Employment Law',
            'consumer': 'Consumer Protection',
            'tax': 'Tax Law',
            'intellectual': 'Intellectual Property',
            'constitutional': 'Constitutional Law',
            'other': 'Other'
        };
        
        card.innerHTML = `
            <div class="inquiry-header">
                <div class="inquiry-id">${this.escapeHtml(inquiry.inquiry_id)}</div>
                <div class="inquiry-status ${inquiry.status}">${inquiry.status}</div>
            </div>
            
            <div class="inquiry-info">
                <div class="info-item">
                    <div class="info-label">Name</div>
                    <div class="info-value">${this.escapeHtml(inquiry.full_name)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Phone</div>
                    <div class="info-value">
                        <a href="tel:${inquiry.phone_number}" style="color: #667eea; text-decoration: none;">
                            ${this.escapeHtml(inquiry.phone_number)}
                        </a>
                    </div>
                </div>
                ${inquiry.email ? `
                <div class="info-item">
                    <div class="info-label">Email</div>
                    <div class="info-value">
                        <a href="mailto:${inquiry.email}" style="color: #667eea; text-decoration: none;">
                            ${this.escapeHtml(inquiry.email)}
                        </a>
                    </div>
                </div>
                ` : ''}
                <div class="info-item">
                    <div class="info-label">Location</div>
                    <div class="info-value">${this.escapeHtml(inquiry.city)}, ${this.escapeHtml(inquiry.state)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Case Type</div>
                    <div class="info-value">${caseTypeLabels[inquiry.case_type] || inquiry.case_type}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Urgency</div>
                    <div class="info-value">${urgencyLabels[inquiry.urgency] || inquiry.urgency}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Budget Range</div>
                    <div class="info-value">${this.formatBudgetRange(inquiry.budget_range)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Submitted</div>
                    <div class="info-value">${this.formatDate(inquiry.submitted_at)}</div>
                </div>
            </div>
            
            <div class="inquiry-description">
                <h4>Case Description</h4>
                <p>${this.escapeHtml(inquiry.case_description)}</p>
            </div>
            
            <div class="inquiry-description">
                <h4>Requirements</h4>
                <p>${this.escapeHtml(inquiry.requirements)}</p>
            </div>
            
            <div class="inquiry-description">
                <h4>Expectations</h4>
                <p>${this.escapeHtml(inquiry.expectations)}</p>
            </div>
            
            ${inquiry.additional_notes ? `
            <div class="inquiry-description">
                <h4>Additional Notes</h4>
                <p>${this.escapeHtml(inquiry.additional_notes)}</p>
            </div>
            ` : ''}
            
            <div class="inquiry-actions">
                ${inquiry.status === 'pending' ? `
                    <button class="action-button primary" onclick="adminPanel.updateStatus('${inquiry.inquiry_id}', 'reviewed')">
                        Mark as Reviewed
                    </button>
                ` : ''}
                ${inquiry.status === 'reviewed' ? `
                    <button class="action-button success" onclick="adminPanel.updateStatus('${inquiry.inquiry_id}', 'contacted')">
                        Mark as Contacted
                    </button>
                ` : ''}
                ${inquiry.status === 'contacted' ? `
                    <button class="action-button secondary" onclick="adminPanel.updateStatus('${inquiry.inquiry_id}', 'closed')">
                        Close Inquiry
                    </button>
                ` : ''}
                <button class="action-button secondary" onclick="adminPanel.viewDetails('${inquiry.inquiry_id}')">
                    View Full Details
                </button>
                <button class="action-button danger" onclick="adminPanel.deleteInquiry('${inquiry.inquiry_id}')">
                    Delete
                </button>
            </div>
        `;
        
        return card;
    }

    /**
     * Update inquiry status
     */
    async updateStatus(inquiryId, newStatus) {
        if (!confirm(`Are you sure you want to update this inquiry to "${newStatus}"?`)) {
            return;
        }
        
        try {
            const response = await fetch(
                `${this.apiBaseUrl}/api/inquiries/${inquiryId}/status?status=${newStatus}`,
                { method: 'PATCH' }
            );
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            // Reload data
            await this.loadData();
            
        } catch (error) {
            console.error('Error updating status:', error);
            alert('Failed to update inquiry status. Please try again.');
        }
    }

    /**
     * Delete inquiry
     */
    async deleteInquiry(inquiryId) {
        if (!confirm('Are you sure you want to delete this inquiry? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(
                `${this.apiBaseUrl}/api/inquiries/${inquiryId}`,
                { method: 'DELETE' }
            );
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            // Reload data
            await this.loadData();
            
        } catch (error) {
            console.error('Error deleting inquiry:', error);
            alert('Failed to delete inquiry. Please try again.');
        }
    }

    /**
     * View full inquiry details
     */
    async viewDetails(inquiryId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/inquiries/${inquiryId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const inquiry = await response.json();
            
            // Create a formatted details view
            const details = `
Inquiry ID: ${inquiry.inquiry_id}
Status: ${inquiry.status}

=== Personal Information ===
Name: ${inquiry.full_name}
Phone: ${inquiry.phone_number}
Email: ${inquiry.email || 'Not provided'}
Location: ${inquiry.city}, ${inquiry.state}

=== Case Information ===
Case Type: ${inquiry.case_type}
Case ID: ${inquiry.case_id || 'Not provided'}
Urgency: ${inquiry.urgency}
Preferred Date: ${inquiry.preferred_date || 'Not specified'}
Previous Lawyer: ${inquiry.previous_lawyer}

=== Description ===
${inquiry.case_description}

=== Requirements ===
${inquiry.requirements}

=== Expectations ===
${inquiry.expectations}

=== Budget ===
${this.formatBudgetRange(inquiry.budget_range)}

=== Additional Notes ===
${inquiry.additional_notes || 'None'}

=== Timestamps ===
Submitted: ${this.formatDate(inquiry.submitted_at)}
Created: ${this.formatDate(inquiry.created_at)}
            `.trim();
            
            alert(details);
            
        } catch (error) {
            console.error('Error loading inquiry details:', error);
            alert('Failed to load inquiry details. Please try again.');
        }
    }

    /**
     * Format budget range for display
     */
    formatBudgetRange(range) {
        const ranges = {
            'under-10k': 'Under ₹10,000',
            '10k-25k': '₹10,000 - ₹25,000',
            '25k-50k': '₹25,000 - ₹50,000',
            '50k-1l': '₹50,000 - ₹1,00,000',
            '1l-2l': '₹1,00,000 - ₹2,00,000',
            '2l-5l': '₹2,00,000 - ₹5,00,000',
            'above-5l': 'Above ₹5,00,000',
            'flexible': 'Flexible'
        };
        
        return ranges[range] || range;
    }

    /**
     * Format date for display
     */
    formatDate(dateString) {
        try {
            const date = new Date(dateString);
            return date.toLocaleString('en-IN', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            return dateString;
        }
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Show loading state
     */
    showLoading() {
        this.inquiriesContainer.style.display = 'none';
        this.emptyState.style.display = 'none';
        this.loadingState.style.display = 'block';
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        this.loadingState.style.display = 'none';
        this.inquiriesContainer.style.display = 'block';
    }

    /**
     * Show empty state
     */
    showEmpty() {
        this.inquiriesContainer.style.display = 'none';
        this.emptyState.style.display = 'block';
    }

    /**
     * Hide empty state
     */
    hideEmpty() {
        this.emptyState.style.display = 'none';
    }

    /**
     * Show error message
     */
    showError(message) {
        alert(message);
    }
}

// Initialize admin panel when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminPanel = new AdminPanel();
});
