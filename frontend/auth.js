const API_BASE = '/api/v1';
let authToken = sessionStorage.getItem('parroquia_token');

// Auth Guard: If no token, redirect to login
if (!authToken && !window.location.pathname.endsWith('login.html')) {
    window.location.href = 'login.html';
}

async function authFetch(url, options = {}) {
    if (!options.headers) options.headers = {};
    if (authToken) {
        options.headers['Authorization'] = `Bearer ${authToken}`;
    }
    if (!(options.body instanceof FormData) && !options.headers['Content-Type']) {
        options.headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(url, options);
    
    if (response.status === 401) {
        logout();
        throw new Error('Sesión expirada');
    }
    
    return response;
}

function logout() {
    authToken = null;
    sessionStorage.removeItem('parroquia_token');
    showToast('Sesión cerrada correctamente', 'success');
    setTimeout(() => {
        window.location.href = 'login.html';
    }, 1000);
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return; // Silent if no container
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'success' ? '<i class="fas fa-check-circle success"></i>' : '<i class="fas fa-exclamation-circle error"></i>';
    toast.innerHTML = `${icon}<span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
