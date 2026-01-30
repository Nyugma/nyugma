/**
 * Legal Case Inquiry Form Handler
 * Handles form submission and validation for legal inquiries
 */

class InquiryFormHandler {
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
        this.loadCaseIdFromUrl();
    }

    /**
     * Initialize DOM element references
     */
    initializeElements() {
        this.inquiryForm = document.getElementById('inquiryForm');
        this.submitButton = document.getElementById('submitInquiry');
        this.successContainer = document.getElementById('successContainer');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.successDetails = document.getElementById('successDetails');
        
        // Form fields
        this.caseIdInput = document.getElementById('caseId');
        this.caseTypeInput = document.getElementById('caseType');
        this.fullNameInput = document.getElementById('fullName');
        this.phoneNumberInput = document.getElementById('phoneNumber');
        this.emailInput = document.getElementById('email');
        this.cityInput = document.getElementById('city');
        this.stateInput = document.getElementById('state');
        this.caseDescriptionInput = document.getElementById('caseDescription');
        this.requirementsInput = document.getElementById('requirements');
        this.expectationsInput = document.getElementById('expectations');
        this.urgencyInput = document.getElementById('urgency');
        this.preferredDateInput = document.getElementById('preferredDate');
        this.budgetRangeInput = document.getElementById('budgetRange');
        this.additionalNotesInput = document.getElementById('additionalNotes');
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        this.inquiryForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        
        // Phone number formatting
        this.phoneNumberInput.addEventListener('input', (e) => this.formatPhoneNumber(e));
        
        // Set minimum date for preferred date (today)
        const today = new Date().toISOString().split('T')[0];
        this.preferredDateInput.setAttribute('min', today);
    }

    /**
     * Load case ID from URL parameter if present
     */
    loadCaseIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        const caseId = urlParams.get('caseId');
        
        if (caseId) {
            this.caseIdInput.value = caseId;
            this.caseIdInput.readOnly = true;
            this.caseIdInput.style.background = '#f9fafb';
        }
    }

    /**
     * Format phone number as user types
     */
    formatPhoneNumber(e) {
        let value = e.target.value.replace(/\D/g, '');
        
        // Add +91 prefix if not present and number starts
        if (value.length > 0 && !value.startsWith('91')) {
            value = '91' + value;
        }
        
        // Limit to 12 digits (91 + 10 digits)
        if (value.length > 12) {
            value = value.substring(0, 12);
        }
        
        // Format: +91 XXXXX XXXXX
        let formatted = '';
        if (value.length > 0) {
            formatted = '+' + value.substring(0, 2);
        }
        if (value.length > 2) {
            formatted += ' ' + value.substring(2, 7);
        }
        if (value.length > 7) {
            formatted += ' ' + value.substring(7, 12);
        }
        
        e.target.value = formatted;
    }

    /**
     * Handle form submission
     */
    async handleFormSubmit(e) {
        e.preventDefault();
        
        // Validate form
        if (!this.inquiryForm.checkValidity()) {
            this.inquiryForm.reportValidity();
            return;
        }

        // Collect form data
        const formData = this.collectFormData();
        
        // Submit inquiry
        await this.submitInquiry(formData);
    }

    /**
     * Collect form data
     */
    collectFormData() {
        const previousLawyerRadio = document.querySelector('input[name="previousLawyer"]:checked');
        
        return {
            case_id: this.caseIdInput.value.trim() || null,
            case_type: this.caseTypeInput.value,
            full_name: this.fullNameInput.value.trim(),
            phone_number: this.phoneNumberInput.value.trim(),
            email: this.emailInput.value.trim() || null,
            city: this.cityInput.value.trim(),
            state: this.stateInput.value,
            case_description: this.caseDescriptionInput.value.trim(),
            requirements: this.requirementsInput.value.trim(),
            expectations: this.expectationsInput.value.trim(),
            urgency: this.urgencyInput.value,
            preferred_date: this.preferredDateInput.value || null,
            previous_lawyer: previousLawyerRadio ? previousLawyerRadio.value : 'no',
            budget_range: this.budgetRangeInput.value,
            additional_notes: this.additionalNotesInput.value.trim() || null
        };
    }

    /**
     * Submit inquiry to backend
     */
    async submitInquiry(formData) {
        try {
            this.showLoading();
            
            const response = await fetch(`${this.apiBaseUrl}/api/inquiries`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || data.message || `HTTP ${response.status}: ${response.statusText}`);
            }

            this.hideLoading();
            this.showSuccess(data);

        } catch (error) {
            console.error('Submission error:', error);
            this.hideLoading();
            this.showError(error);
        }
    }

    /**
     * Show loading state
     */
    showLoading() {
        this.loadingOverlay.style.display = 'flex';
        this.submitButton.disabled = true;
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        this.loadingOverlay.style.display = 'none';
        this.submitButton.disabled = false;
    }

    /**
     * Show success message
     */
    showSuccess(data) {
        // Hide form
        this.inquiryForm.style.display = 'none';
        
        // Show success container
        this.successContainer.style.display = 'block';
        
        // Populate success details
        this.successDetails.innerHTML = `
            <p><strong>Inquiry ID:</strong> ${data.inquiry_id}</p>
            <p><strong>Name:</strong> ${data.full_name}</p>
            <p><strong>Phone:</strong> ${data.phone_number}</p>
            <p><strong>Case Type:</strong> ${this.formatCaseType(data.case_type)}</p>
            <p><strong>Status:</strong> <span style="color: #059669; font-weight: 600;">Pending Review</span></p>
        `;
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    /**
     * Show error message
     */
    showError(error) {
        let errorMessage = 'An error occurred while submitting your inquiry. Please try again.';
        
        // Check for CORS errors
        if (error.message.includes('Failed to fetch') || 
            error.message.includes('NetworkError') ||
            error.message.includes('CORS')) {
            errorMessage = 'Unable to connect to the server. Please check your internet connection and try again.';
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        alert(errorMessage);
    }

    /**
     * Format case type for display
     */
    formatCaseType(caseType) {
        const caseTypes = {
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
        
        return caseTypes[caseType] || caseType;
    }
}

// Initialize the form handler when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.inquiryHandler = new InquiryFormHandler();
});
