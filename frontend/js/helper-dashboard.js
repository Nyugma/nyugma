/**
 * Helper Dashboard - Add Case Functionality
 */

// Require authentication and helper user type
if (!requireUserType('helper')) {
    // Will redirect if not authenticated or not a helper
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('helperCaseForm');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const successContainer = document.getElementById('successContainer');
    const submitButton = document.getElementById('submitCase');

    // Form submission handler
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate form
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        // Get form data
        const formData = new FormData();
        
        // Add file
        const fileInput = document.getElementById('caseDocument');
        if (fileInput.files.length === 0) {
            alert('Please select a PDF document');
            return;
        }
        formData.append('file', fileInput.files[0]);
        
        // Add case metadata
        const caseMetadata = {
            user_id: getCurrentUser().user_id, // Use authenticated user ID
            title: document.getElementById('caseTitle').value,
            case_type: document.getElementById('caseType').value,
            description: document.getElementById('description').value,
            outcome: document.getElementById('outcome').value,
            duration_months: parseInt(document.getElementById('durationMonths').value),
            total_cost: parseFloat(document.getElementById('totalCost').value),
            court_name: document.getElementById('courtName').value,
            state: document.getElementById('state').value,
            city: document.getElementById('city').value,
            lawyer_name: document.getElementById('lawyerName').value || null,
            lawyer_contact: document.getElementById('lawyerContact').value || null,
            key_learnings: document.getElementById('keyLearnings').value || null,
            advice_for_others: document.getElementById('adviceForOthers').value || null,
            is_public: document.getElementById('isPublic').checked,
            willing_to_help: document.getElementById('willingToHelp').checked
        };
        
        formData.append('metadata', JSON.stringify(caseMetadata));

        // Show loading
        form.style.display = 'none';
        loadingOverlay.style.display = 'flex';
        submitButton.disabled = true;

        try {
            // Get backend URL
            const backendUrl = getBackendUrl();
            
            // Submit to API with authentication
            const response = await authenticatedFetch(`${backendUrl}/api/helper/cases`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to submit case');
            }

            const result = await response.json();
            
            // Hide loading
            loadingOverlay.style.display = 'none';
            
            // Show success message
            displaySuccess(result);
            
        } catch (error) {
            console.error('Error submitting case:', error);
            
            // Hide loading
            loadingOverlay.style.display = 'none';
            form.style.display = 'block';
            submitButton.disabled = false;
            
            // Show error
            alert('Error submitting case: ' + error.message);
        }
    });

    /**
     * Display success message
     */
    function displaySuccess(result) {
        const successDetails = document.getElementById('successDetails');
        
        successDetails.innerHTML = `
            <div style="text-align: left; margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                <p><strong>Case ID:</strong> ${result.case_id}</p>
                <p><strong>Title:</strong> ${result.title}</p>
                <p><strong>Type:</strong> ${result.case_type}</p>
                <p><strong>Outcome:</strong> ${result.outcome}</p>
                <p><strong>Status:</strong> Your case has been processed and added to the database</p>
                ${result.similar_cases_count ? `<p><strong>Similar Cases Found:</strong> ${result.similar_cases_count}</p>` : ''}
            </div>
        `;
        
        successContainer.style.display = 'block';
    }

    // File input validation
    const fileInput = document.getElementById('caseDocument');
    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            // Check file type
            if (file.type !== 'application/pdf') {
                alert('Please select a PDF file');
                this.value = '';
                return;
            }
            
            // Check file size (10MB max)
            const maxSize = 10 * 1024 * 1024; // 10MB in bytes
            if (file.size > maxSize) {
                alert('File size must be less than 10MB');
                this.value = '';
                return;
            }
        }
    });

    // Cost input formatting
    const costInput = document.getElementById('totalCost');
    costInput.addEventListener('blur', function() {
        if (this.value) {
            const value = parseFloat(this.value);
            if (!isNaN(value)) {
                this.value = Math.round(value);
            }
        }
    });
});
