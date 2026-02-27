/**
 * Legal Case Similarity Web Application
 * Frontend JavaScript for API communication and user interaction
 * 
 * Requirements: 4.3, 4.4, 4.5 - API communication, result display, error handling
 */

// Require authentication before using the app
if (!requireAuth()) {
    // Will redirect to login if not authenticated
}

class LegalCaseSimilarityApp {
    constructor() {
        // Validate and initialize configuration
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
            this.showError(
                'Application configuration error. Please contact the administrator.'
            );
            throw error;
        }
        
        this.maxFileSize = 10 * 1024 * 1024; // 10MB
        this.allowedFileTypes = ['application/pdf'];
        this.currentUpload = null;
        
        this.initializeElements();
        this.bindEvents();
        this.setupDragAndDrop();
    }

    /**
     * Initialize DOM element references
     */
    initializeElements() {
        // Form elements
        this.uploadForm = document.getElementById('uploadForm');
        this.fileInput = document.getElementById('fileInput');
        this.fileInputLabel = document.querySelector('.file-input-label');
        this.submitButton = document.getElementById('submitButton');
        
        // File display elements
        this.selectedFile = document.getElementById('selectedFile');
        this.fileName = document.getElementById('fileName');
        this.fileSize = document.getElementById('fileSize');
        this.removeFileButton = document.getElementById('removeFile');
        
        // Loading elements
        this.loadingContainer = document.getElementById('loadingContainer');
        this.progressSteps = {
            step1: document.getElementById('step1'),
            step2: document.getElementById('step2'),
            step3: document.getElementById('step3')
        };
        
        // Results elements
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsMeta = document.getElementById('resultsMeta');
        this.resultsContainer = document.getElementById('resultsContainer');
        
        // Error elements
        this.errorSection = document.getElementById('errorSection');
        this.errorMessage = document.getElementById('errorMessage');
        this.retryButton = document.getElementById('retryButton');
        
        // Empty results elements
        this.emptyResultsSection = document.getElementById('emptyResultsSection');
        this.uploadAnotherButton = document.getElementById('uploadAnotherButton');
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Form submission
        this.uploadForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        
        // File input change
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Remove file button
        this.removeFileButton.addEventListener('click', () => this.clearFileSelection());
        
        // Retry button
        this.retryButton.addEventListener('click', () => this.resetToUploadState());
        
        // Upload another button
        this.uploadAnotherButton.addEventListener('click', () => this.resetToUploadState());
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.addEventListener(eventName, this.preventDefaults, false);
        });
    }

    /**
     * Setup drag and drop functionality
     */
    setupDragAndDrop() {
        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            this.fileInputLabel.addEventListener(eventName, () => {
                this.fileInputLabel.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.fileInputLabel.addEventListener(eventName, () => {
                this.fileInputLabel.classList.remove('dragover');
            }, false);
        });

        // Handle dropped files
        this.fileInputLabel.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.fileInput.files = files;
                this.handleFileSelect({ target: { files } });
            }
        }, false);
    }

    /**
     * Prevent default drag behaviors
     */
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    /**
     * Handle form submission
     */
    async handleFormSubmit(e) {
        e.preventDefault();
        
        if (!this.fileInput.files[0]) {
            this.showError('Please select a PDF file to upload.');
            return;
        }

        const file = this.fileInput.files[0];
        
        // Validate file before upload
        if (!this.validateFile(file)) {
            return;
        }

        await this.uploadFile(file);
    }

    /**
     * Handle file selection
     */
    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            const file = files[0];
            if (this.validateFile(file)) {
                this.displaySelectedFile(file);
            } else {
                this.clearFileSelection();
            }
        }
    }

    /**
     * Validate selected file
     */
    validateFile(file) {
        // Check file type
        if (!this.allowedFileTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.pdf')) {
            this.showError('Please select a PDF file. Only PDF files are supported.');
            return false;
        }

        // Check file size
        if (file.size > this.maxFileSize) {
            const maxSizeMB = this.maxFileSize / (1024 * 1024);
            this.showError(`File size (${this.formatFileSize(file.size)}) exceeds the maximum allowed size of ${maxSizeMB}MB.`);
            return false;
        }

        // Check if file is empty
        if (file.size === 0) {
            this.showError('The selected file appears to be empty. Please select a valid PDF file.');
            return false;
        }

        return true;
    }

    /**
     * Display selected file information
     */
    displaySelectedFile(file) {
        this.fileName.textContent = file.name;
        this.fileSize.textContent = this.formatFileSize(file.size);
        this.selectedFile.style.display = 'flex';
        this.fileInputLabel.style.display = 'none';
    }

    /**
     * Clear file selection
     */
    clearFileSelection() {
        this.fileInput.value = '';
        this.selectedFile.style.display = 'none';
        this.fileInputLabel.style.display = 'block';
        this.fileInputLabel.classList.remove('dragover');
    }

    /**
     * Format file size for display
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Upload file and process results
     */
    async uploadFile(file) {
        try {
            this.showLoading();
            
            const formData = new FormData();
            formData.append('file', file);

            // Simulate progress steps
            this.updateProgressStep(1);
            
            // Use enhanced search endpoint with authentication
            const response = await authenticatedFetch(`${this.apiBaseUrl}/api/search/enhanced`, {
                method: 'POST',
                body: formData
            });

            this.updateProgressStep(2);

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `HTTP ${response.status}: ${response.statusText}`);
            }

            this.updateProgressStep(3);
            
            // Small delay to show final step
            await new Promise(resolve => setTimeout(resolve, 500));

            this.hideLoading();
            this.displayResults(data);

        } catch (error) {
            console.error('Upload error:', error);
            this.hideLoading();
            this.showError(this.getErrorMessage(error));
        }
    }

    /**
     * Get user-friendly error message
     */
    getErrorMessage(error) {
        // Check for CORS errors
        if (error.message.includes('Failed to fetch') || 
            error.message.includes('NetworkError') ||
            error.message.includes('CORS')) {
            return 'Unable to connect to the API. This may be a configuration or network issue. ' +
                   'Please check that the backend URL is correct and CORS is properly configured. ' +
                   'If you are a developer, check the browser console for more details.';
        }
        
        if (error.message.includes('413')) {
            return 'The file is too large. Please select a smaller PDF file (maximum 10MB).';
        }
        
        if (error.message.includes('400')) {
            return 'Invalid file format. Please select a valid PDF file.';
        }
        
        if (error.message.includes('422')) {
            return 'Unable to process the PDF file. The file may be corrupted or password-protected.';
        }
        
        if (error.message.includes('500')) {
            return 'A server error occurred. Please try again later or contact support if the problem persists.';
        }
        
        return error.message || 'An unexpected error occurred. Please try again.';
    }

    /**
     * Show loading state with progress steps
     */
    showLoading() {
        this.hideAllSections();
        this.loadingContainer.style.display = 'block';
        this.loadingContainer.classList.add('fade-in');
        this.submitButton.disabled = true;
        
        // Reset progress steps
        Object.values(this.progressSteps).forEach(step => {
            step.classList.remove('active');
        });
    }

    /**
     * Update progress step
     */
    updateProgressStep(stepNumber) {
        // Activate current step
        if (this.progressSteps[`step${stepNumber}`]) {
            this.progressSteps[`step${stepNumber}`].classList.add('active');
        }
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        this.loadingContainer.style.display = 'none';
        this.submitButton.disabled = false;
    }

    /**
     * Display search results
     */
    displayResults(data) {
        this.hideAllSections();
        
        if (!data.results || data.results.length === 0) {
            this.showEmptyResults();
            return;
        }

        // Update results metadata
        const processingTime = data.processing_time ? data.processing_time.toFixed(2) : 'N/A';
        const helperCasesCount = data.helper_cases_count || 0;
        const originalCasesCount = data.original_cases_count || 0;
        
        this.resultsMeta.innerHTML = `
            <div class="results-stats">
                <span><strong>${data.results.length}</strong> similar cases found</span>
                <span>•</span>
                <span>Processed in <strong>${processingTime}s</strong></span>
                <span>•</span>
                <span><strong>${helperCasesCount}</strong> from helpers</span>
                <span>•</span>
                <span><strong>${originalCasesCount}</strong> from database</span>
            </div>
        `;

        // Clear previous results
        this.resultsContainer.innerHTML = '';

        // Display each result
        data.results.forEach((caseResult, index) => {
            const caseElement = this.createCaseResultElement(caseResult, index + 1);
            this.resultsContainer.appendChild(caseElement);
        });

        this.resultsSection.style.display = 'block';
        this.resultsSection.classList.add('fade-in');
    }

    /**
     * Create a case result element
     */
    createCaseResultElement(caseResult, rank) {
        const caseDiv = document.createElement('div');
        caseDiv.className = 'case-result';
        
        const similarityPercentage = (caseResult.similarity_score * 100).toFixed(1);
        const formattedDate = caseResult.date ? this.formatDate(caseResult.date) : 'N/A';
        const isHelperCase = caseResult.source === 'helper' && caseResult.helper_info;
        
        // Build helper profile section if available
        let helperProfileHTML = '';
        if (isHelperCase) {
            const helper = caseResult.helper_info;
            const reputationStars = this.generateStars(helper.reputation_score || 0);
            
            helperProfileHTML = `
                <div class="helper-profile">
                    <div class="helper-badge">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                        Experienced Helper
                    </div>
                    <div class="helper-info-grid">
                        <div class="helper-info-item">
                            <strong>${this.escapeHtml(helper.full_name || 'Anonymous')}</strong>
                            <div class="helper-reputation">
                                ${reputationStars}
                                <span class="reputation-text">(${helper.total_ratings || 0} ratings)</span>
                            </div>
                        </div>
                        <div class="helper-info-item">
                            <span class="info-label">Cases Helped:</span>
                            <span class="info-value">${helper.cases_helped || 0}</span>
                        </div>
                        <div class="helper-info-item">
                            <span class="info-label">Location:</span>
                            <span class="info-value">${this.escapeHtml(helper.city || 'N/A')}, ${this.escapeHtml(helper.state || 'N/A')}</span>
                        </div>
                    </div>
                    ${caseResult.outcome ? `
                        <div class="case-outcome">
                            <span class="outcome-label">Outcome:</span>
                            <span class="outcome-badge outcome-${caseResult.outcome.toLowerCase()}">${this.escapeHtml(caseResult.outcome)}</span>
                        </div>
                    ` : ''}
                    ${caseResult.total_cost ? `
                        <div class="case-cost">
                            <span class="cost-label">Total Cost:</span>
                            <span class="cost-value">₹${this.formatCurrency(caseResult.total_cost)}</span>
                            ${caseResult.duration_months ? `<span class="duration">(${caseResult.duration_months} months)</span>` : ''}
                        </div>
                    ` : ''}
                    ${caseResult.advice_for_others ? `
                        <div class="helper-advice">
                            <strong>Advice:</strong>
                            <p>${this.escapeHtml(caseResult.advice_for_others)}</p>
                        </div>
                    ` : ''}
                </div>
            `;
        }
        
        caseDiv.innerHTML = `
            <div class="case-header">
                <div class="case-info">
                    <h3 class="case-title">${this.escapeHtml(caseResult.title)}</h3>
                    <div class="case-meta">
                        ${!isHelperCase ? `
                            <div class="case-date">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                                    <line x1="16" y1="2" x2="16" y2="6"></line>
                                    <line x1="8" y1="2" x2="8" y2="6"></line>
                                    <line x1="3" y1="10" x2="21" y2="10"></line>
                                </svg>
                                ${formattedDate}
                            </div>
                        ` : `
                            <div class="case-type">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                    <polyline points="14 2 14 8 20 8"></polyline>
                                </svg>
                                ${this.escapeHtml(caseResult.case_type || 'N/A')}
                            </div>
                        `}
                        <div class="similarity-score">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"></polygon>
                            </svg>
                            <span class="similarity-badge">${similarityPercentage}% match</span>
                        </div>
                    </div>
                </div>
                ${isHelperCase && caseResult.helper_info.willing_to_help ? `
                    <div class="case-quick-actions">
                        <button class="icon-button connect-button" onclick="app.requestConnection('${caseResult.helper_info.user_id}')" title="Request connection" aria-label="Request connection">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                                <circle cx="9" cy="7" r="4"></circle>
                                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                            </svg>
                        </button>
                    </div>
                ` : `
                    <div class="case-quick-actions">
                        <a href="tel:+919913816941" class="icon-button call-button" title="Call for consultation" aria-label="Call for consultation">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                            </svg>
                        </a>
                        <button class="icon-button schedule-button" onclick="app.scheduleInquiry('${caseResult.case_id}')" title="Schedule inquiry" aria-label="Schedule inquiry">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                                <line x1="16" y1="2" x2="16" y2="6"></line>
                                <line x1="8" y1="2" x2="8" y2="6"></line>
                                <line x1="3" y1="10" x2="21" y2="10"></line>
                                <path d="M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01M16 18h.01"></path>
                            </svg>
                        </button>
                    </div>
                `}
            </div>
            
            ${helperProfileHTML}
            
            <div class="case-snippet">
                ${this.escapeHtml(caseResult.snippet || 'No preview available.')}
            </div>
            
            <div class="case-actions">
                ${!isHelperCase ? `
                    <a href="${this.apiBaseUrl}${caseResult.download_url}" class="download-button" target="_blank" rel="noopener noreferrer">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-15"></path>
                            <polyline points="7,10 12,15 17,10"></polyline>
                            <line x1="12" y1="15" x2="12" y2="3"></line>
                        </svg>
                        Download Case
                    </a>
                    <button class="view-details-button" onclick="app.viewCaseDetails('${caseResult.case_id}')">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                        View Details
                    </button>
                ` : `
                    <button class="primary-button" onclick="app.requestConnection('${caseResult.helper_info.user_id}')">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                            <circle cx="9" cy="7" r="4"></circle>
                            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                        </svg>
                        Request Connection
                    </button>
                `}
            </div>
        `;
        
        return caseDiv;
    }

    /**
     * Schedule inquiry - Navigate to inquiry form
     */
    scheduleInquiry(caseId) {
        // Navigate to inquiry page with case ID
        window.location.href = `inquiry.html?caseId=${encodeURIComponent(caseId)}`;
    }

    /**
     * Request connection with a helper
     */
    async requestConnection(helperId) {
        try {
            const currentUser = getCurrentUser();
            if (!currentUser) {
                alert('Please log in to request a connection.');
                window.location.href = 'auth.html';
                return;
            }

            // Show confirmation dialog
            const confirmed = confirm('Would you like to request a connection with this helper? They will be notified and can choose to accept your request.');
            
            if (!confirmed) {
                return;
            }

            // Send connection request to backend
            const response = await authenticatedFetch(`${this.apiBaseUrl}/api/connections/request`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    helper_id: helperId,
                    message: 'I would like to connect with you regarding a similar case.'
                })
            });

            const data = await response.json();

            if (!response.ok) {
                if (response.status === 409) {
                    alert('You already have a pending or accepted connection with this helper.');
                } else {
                    throw new Error(data.message || 'Failed to send connection request');
                }
                return;
            }

            // Show success message
            alert('Connection request sent successfully! The helper will be notified and can accept your request. You can view your pending connections in your dashboard.');
            
            console.log('Connection request sent:', data);
            
        } catch (error) {
            console.error('Error requesting connection:', error);
            alert('Failed to send connection request. Please try again.');
        }
    }

    /**
     * Generate star rating display
     */
    generateStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
        
        let starsHTML = '<div class="stars">';
        
        // Full stars
        for (let i = 0; i < fullStars; i++) {
            starsHTML += '<svg class="star star-full" width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"></polygon></svg>';
        }
        
        // Half star
        if (hasHalfStar) {
            starsHTML += '<svg class="star star-half" width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2"><defs><linearGradient id="half"><stop offset="50%" stop-color="currentColor"/><stop offset="50%" stop-color="transparent"/></linearGradient></defs><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" fill="url(#half)"></polygon></svg>';
        }
        
        // Empty stars
        for (let i = 0; i < emptyStars; i++) {
            starsHTML += '<svg class="star star-empty" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"></polygon></svg>';
        }
        
        starsHTML += '</div>';
        return starsHTML;
    }

    /**
     * Format currency for display
     */
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            maximumFractionDigits: 0
        }).format(amount);
    }

    /**
     * View case details (placeholder for future implementation)
     */
    async viewCaseDetails(caseId) {
        try {
            const casesEndpoint = window.AppConfig.getEndpoint('cases');
            const response = await fetch(`${casesEndpoint}/${caseId}`);
            const caseData = await response.json();
            
            if (response.ok) {
                // For now, just show an alert with case details
                // In a full implementation, this would open a modal or navigate to a details page
                alert(`Case Details:\n\nTitle: ${caseData.title}\nDate: ${caseData.date}\nCase ID: ${caseData.case_id}\n\nThis would normally open a detailed view.`);
            } else {
                throw new Error(caseData.message || 'Failed to load case details');
            }
        } catch (error) {
            console.error('Error loading case details:', error);
            
            // Check for CORS errors
            if (error.message.includes('Failed to fetch') || 
                error.message.includes('NetworkError') ||
                error.message.includes('CORS')) {
                alert('Unable to connect to the API. Please check your configuration and try again.');
            } else {
                alert('Unable to load case details. Please try again later.');
            }
        }
    }

    /**
     * Show empty results state
     */
    showEmptyResults() {
        this.hideAllSections();
        this.emptyResultsSection.style.display = 'block';
        this.emptyResultsSection.classList.add('fade-in');
    }

    /**
     * Show error state
     */
    showError(message) {
        this.hideAllSections();
        this.errorMessage.textContent = message;
        this.errorSection.style.display = 'block';
        this.errorSection.classList.add('fade-in');
    }

    /**
     * Reset to upload state
     */
    resetToUploadState() {
        this.hideAllSections();
        this.clearFileSelection();
        document.querySelector('.upload-section').style.display = 'block';
    }

    /**
     * Hide all sections
     */
    hideAllSections() {
        this.loadingContainer.style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.errorSection.style.display = 'none';
        this.emptyResultsSection.style.display = 'none';
        
        // Remove fade-in classes
        [this.loadingContainer, this.resultsSection, this.errorSection, this.emptyResultsSection].forEach(element => {
            element.classList.remove('fade-in');
        });
    }

    /**
     * Format date for display
     */
    formatDate(dateString) {
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } catch (error) {
            return dateString; // Return original string if parsing fails
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
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new LegalCaseSimilarityApp();
});

// Handle browser back/forward navigation
window.addEventListener('popstate', () => {
    if (window.app) {
        window.app.resetToUploadState();
    }
});

// Handle online/offline status
window.addEventListener('online', () => {
    console.log('Connection restored');
});

window.addEventListener('offline', () => {
    console.log('Connection lost');
    if (window.app) {
        window.app.showError('Internet connection lost. Please check your connection and try again.');
    }
});
