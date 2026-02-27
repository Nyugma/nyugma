/**
 * Authentication functionality - Login and Registration
 */

document.addEventListener('DOMContentLoaded', function() {
    // Tab switching
    const tabs = document.querySelectorAll('.auth-tab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Show corresponding form
            if (targetTab === 'login') {
                loginForm.style.display = 'block';
                registerForm.style.display = 'none';
            } else {
                loginForm.style.display = 'none';
                registerForm.style.display = 'block';
            }
        });
    });
    
    // Password toggle functionality
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const targetId = this.dataset.target;
            const input = document.getElementById(targetId);
            
            if (input.type === 'password') {
                input.type = 'text';
                this.innerHTML = `
                    <svg class="eye-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                        <line x1="1" y1="1" x2="23" y2="23"></line>
                    </svg>
                `;
            } else {
                input.type = 'password';
                this.innerHTML = `
                    <svg class="eye-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                `;
            }
        });
    });
    
    // Login form submission
    const loginFormElement = document.getElementById('loginFormElement');
    const loginButton = document.getElementById('loginButton');
    const loginMessage = document.getElementById('loginMessage');
    
    loginFormElement.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        
        // Show loading state
        loginButton.classList.add('loading');
        loginButton.disabled = true;
        loginMessage.style.display = 'none';
        
        try {
            const backendUrl = getBackendUrl();
            const response = await fetch(`${backendUrl}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                // Handle specific error cases
                if (response.status === 401) {
                    throw new Error('Invalid email or password. Please try again.');
                }
                if (response.status === 404) {
                    throw new Error('Account not found. Please register first.');
                }
                throw new Error(data.detail || 'Login failed');
            }
            
            // Store token and user info
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Show success message
            showMessage(loginMessage, 'success', 'Login successful! Redirecting...');
            
            // Redirect to dashboard or stored redirect URL
            setTimeout(() => {
                const redirectUrl = localStorage.getItem('redirect_after_login');
                if (redirectUrl) {
                    localStorage.removeItem('redirect_after_login');
                    window.location.href = redirectUrl;
                } else {
                    window.location.href = 'dashboard.html';
                }
            }, 1500);
            
        } catch (error) {
            console.error('Login error:', error);
            showMessage(loginMessage, 'error', error.message);
            loginButton.classList.remove('loading');
            loginButton.disabled = false;
        }
    });
    
    // Register form submission
    const registerFormElement = document.getElementById('registerFormElement');
    const registerButton = document.getElementById('registerButton');
    const registerMessage = document.getElementById('registerMessage');
    
    registerFormElement.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = {
            email: document.getElementById('registerEmail').value,
            password: document.getElementById('registerPassword').value,
            full_name: document.getElementById('registerName').value,
            phone: document.getElementById('registerPhone').value || null,
            city: document.getElementById('registerCity').value || null,
            state: document.getElementById('registerState').value || null,
            user_type: document.querySelector('input[name="user_type"]:checked').value
        };
        
        // Validate password
        const passwordValidation = validatePassword(formData.password);
        if (!passwordValidation.valid) {
            showMessage(registerMessage, 'error', passwordValidation.message);
            return;
        }
        
        // Show loading state
        registerButton.classList.add('loading');
        registerButton.disabled = true;
        registerMessage.style.display = 'none';
        
        try {
            const backendUrl = getBackendUrl();
            const response = await fetch(`${backendUrl}/api/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                // Handle specific error cases
                if (response.status === 409) {
                    throw new Error('This email is already registered. Please login instead or use a different email.');
                }
                throw new Error(data.detail || 'Registration failed');
            }
            
            // Store token and user info
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Show success message
            showMessage(registerMessage, 'success', 'Account created successfully! Redirecting...');
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
            
        } catch (error) {
            console.error('Registration error:', error);
            showMessage(registerMessage, 'error', error.message);
            registerButton.classList.remove('loading');
            registerButton.disabled = false;
        }
    });
    
    // Check if already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
        // Verify token is still valid
        verifyToken(token).then(valid => {
            if (valid) {
                window.location.href = 'dashboard.html';
            }
        });
    }
});

/**
 * Show message to user
 */
function showMessage(element, type, message) {
    element.textContent = message;
    element.className = `form-message ${type}`;
    element.style.display = 'block';
}

/**
 * Validate password strength
 */
function validatePassword(password) {
    if (password.length < 8) {
        return {
            valid: false,
            message: 'Password must be at least 8 characters long'
        };
    }
    
    if (!/[A-Z]/.test(password)) {
        return {
            valid: false,
            message: 'Password must contain at least one uppercase letter'
        };
    }
    
    if (!/[a-z]/.test(password)) {
        return {
            valid: false,
            message: 'Password must contain at least one lowercase letter'
        };
    }
    
    if (!/[0-9]/.test(password)) {
        return {
            valid: false,
            message: 'Password must contain at least one number'
        };
    }
    
    return { valid: true, message: '' };
}

/**
 * Verify if token is still valid
 */
async function verifyToken(token) {
    try {
        const backendUrl = getBackendUrl();
        const response = await fetch(`${backendUrl}/api/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        return response.ok;
    } catch (error) {
        return false;
    }
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
 * Logout user
 */
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = 'auth.html';
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}
