// BloodCircle - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Loading spinner for form submissions
    const submitButtons = document.querySelectorAll('form button[type="submit"]');
    submitButtons.forEach(button => {
        button.closest('form').addEventListener('submit', function() {
            const spinner = document.getElementById('loadingSpinner');
            if (spinner) {
                spinner.style.display = 'flex';
            }
            button.disabled = true;
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
        });
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm="delete"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // OTP input auto-focus
    const otpInput = document.getElementById('otp');
    if (otpInput) {
        otpInput.addEventListener('input', function(e) {
            // Only allow numbers
            this.value = this.value.replace(/[^0-9]/g, '');
            
            // Auto-submit when 6 digits are entered
            if (this.value.length === 6) {
                // Optional: Auto-submit form
                // this.closest('form').submit();
            }
        });
    }

    // Phone number formatting
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            // Remove non-numeric characters except + at the start
            let value = this.value.replace(/[^\d+]/g, '');
            if (value.length > 1) {
                value = value.replace(/\+/g, '');
                value = '+' + value;
            }
            this.value = value;
        });
    });

    // Password strength indicator
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            const strengthBar = document.getElementById('passwordStrength');
            
            if (strengthBar) {
                let strength = 0;
                if (password.length >= 8) strength++;
                if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
                if (/\d/.test(password)) strength++;
                if (/[^a-zA-Z\d]/.test(password)) strength++;
                
                const strengthText = ['Weak', 'Fair', 'Good', 'Strong'];
                const strengthColor = ['danger', 'warning', 'info', 'success'];
                
                strengthBar.className = `progress-bar bg-${strengthColor[strength]}`;
                strengthBar.style.width = `${(strength + 1) * 25}%`;
                strengthBar.textContent = strengthText[strength];
            }
        });
    }

    // Search functionality with debounce
    const searchInputs = document.querySelectorAll('input[type="search"]');
    searchInputs.forEach(input => {
        let timeout = null;
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                // Trigger search
                const form = this.closest('form');
                if (form) {
                    form.submit();
                }
            }, 500);
        });
    });

    // Smooth scroll to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Counter animation for statistics
    const counters = document.querySelectorAll('.counter');
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const updateCounter = () => {
            current += step;
            if (current < target) {
                counter.textContent = Math.ceil(current);
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };
        
        // Start animation when element is in viewport
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateCounter();
                    observer.unobserve(entry.target);
                }
            });
        });
        
        observer.observe(counter);
    });

    // Date picker - set min date to today
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    dateInputs.forEach(input => {
        if (input.id === 'required_by_date') {
            input.setAttribute('min', today);
        }
        if (input.id === 'date_of_birth') {
            // Set max date for DOB (18 years ago)
            const eighteenYearsAgo = new Date();
            eighteenYearsAgo.setFullYear(eighteenYearsAgo.getFullYear() - 18);
            input.setAttribute('max', eighteenYearsAgo.toISOString().split('T')[0]);
        }
    });

    // Toggle password visibility
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });

    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const preview = document.getElementById('preview');
            if (preview && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });

    // Blood group compatibility checker
    window.checkCompatibility = function(donorBloodGroup, recipientBloodGroup) {
        const compatibility = {
            'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
            'O+': ['O+', 'A+', 'B+', 'AB+'],
            'A-': ['A-', 'A+', 'AB-', 'AB+'],
            'A+': ['A+', 'AB+'],
            'B-': ['B-', 'B+', 'AB-', 'AB+'],
            'B+': ['B+', 'AB+'],
            'AB-': ['AB-', 'AB+'],
            'AB+': ['AB+']
        };
        
        return compatibility[donorBloodGroup] && 
               compatibility[donorBloodGroup].includes(recipientBloodGroup);
    };

    // Initialize charts if Chart.js is loaded
    if (typeof Chart !== 'undefined') {
        const chartElements = document.querySelectorAll('[data-chart]');
        chartElements.forEach(element => {
            const type = element.getAttribute('data-chart');
            const data = JSON.parse(element.getAttribute('data-chart-data'));
            
            new Chart(element, {
                type: type,
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        });
    }

    // Print functionality
    const printButtons = document.querySelectorAll('[data-print]');
    printButtons.forEach(button => {
        button.addEventListener('click', function() {
            window.print();
        });
    });

    // Copy to clipboard
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const text = this.getAttribute('data-copy');
            navigator.clipboard.writeText(text).then(() => {
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            });
        });
    });
});

// Utility functions
function showLoading() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.style.display = 'flex';
    }
}

function hideLoading() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.style.display = 'none';
    }
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        return;
    }
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}
