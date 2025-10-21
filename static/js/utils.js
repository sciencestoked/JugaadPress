/* ===== JUGAADPRESS - SHARED UTILITIES ===== */

/**
 * Show loading overlay with custom message
 */
function showLoading(message = 'Loading...') {
    const overlay = document.getElementById('loadingOverlay');
    const text = document.getElementById('loadingText');
    if (overlay && text) {
        text.textContent = message;
        overlay.classList.add('show');
    }
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('show');
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = toast.querySelector('i');

    if (!toast || !toastMessage) return;

    // Set message
    toastMessage.textContent = message;

    // Set icon and style
    if (type === 'success') {
        toastIcon.className = 'fas fa-check-circle';
        toast.classList.remove('error');
        toast.classList.add('success');
    } else if (type === 'error') {
        toastIcon.className = 'fas fa-exclamation-circle';
        toast.classList.remove('success');
        toast.classList.add('error');
    }

    // Show toast
    toast.classList.add('show');

    // Hide after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

/**
 * Show modal dialog
 */
function showModal(title, message, onConfirm, onCancel = null) {
    const modalOverlay = document.getElementById('modal-overlay');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const confirmBtn = document.getElementById('modal-confirm');
    const cancelBtn = document.getElementById('modal-cancel');

    if (!modalOverlay) return;

    modalTitle.textContent = title;
    modalMessage.textContent = message;
    modalOverlay.classList.add('show');

    const handleConfirm = () => {
        onConfirm();
        modalOverlay.classList.remove('show');
        cleanup();
    };

    const handleCancel = () => {
        if (onCancel) onCancel();
        modalOverlay.classList.remove('show');
        cleanup();
    };

    const handleOverlayClick = (e) => {
        if (e.target === modalOverlay) handleCancel();
    };

    const cleanup = () => {
        confirmBtn.removeEventListener('click', handleConfirm);
        cancelBtn.removeEventListener('click', handleCancel);
        modalOverlay.removeEventListener('click', handleOverlayClick);
    };

    confirmBtn.addEventListener('click', handleConfirm);
    cancelBtn.addEventListener('click', handleCancel);
    modalOverlay.addEventListener('click', handleOverlayClick);
}

/**
 * API call with retry logic
 */
async function apiCall(url, options = {}, retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API call failed (attempt ${i + 1}/${retries}):`, error);
            if (i === retries - 1) throw error;
            // Wait before retry (exponential backoff)
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
        }
    }
}

/**
 * Load and personalize user info (for dashboard and editor)
 */
async function loadUserPersonalization(subtitleElementId) {
    try {
        const response = await fetch('/api/user');
        if (response.ok) {
            const user = await response.json();
            if (user.name) {
                const firstName = user.name.split(' ')[0].toLowerCase();
                const subtitleEl = document.getElementById(subtitleElementId);
                if (subtitleEl) {
                    subtitleEl.innerHTML = `// <span style="color: #ff6b6b; text-shadow: 0 0 10px rgba(255, 107, 107, 0.4);">@${firstName}</span>`;
                }
            }
            return user;
        }
    } catch (error) {
        // Silent fail - user info is optional
        console.error('Could not load user info:', error);
    }
    return null;
}

/**
 * Format date relative to now
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'today';
    if (days === 1) return 'yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Get book name from URL parameter
 */
function getBookFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('book');
}

/**
 * Build API URL with book parameter
 */
function apiUrl(endpoint, bookName, includeBook = true) {
    if (includeBook && bookName && !endpoint.includes('?')) {
        return `${endpoint}?book=${encodeURIComponent(bookName)}`;
    } else if (includeBook && bookName && endpoint.includes('?')) {
        return `${endpoint}&book=${encodeURIComponent(bookName)}`;
    }
    return endpoint;
}
