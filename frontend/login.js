const API_BASE = '/api/v1';

window.addEventListener('load', () => {
    // If already logged in, go to dashboard
    if (localStorage.getItem('parroquia_token')) {
        window.location.href = 'index.html';
    }
});

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const btn = document.getElementById('btn-login');
    const btnText = document.getElementById('btn-text');
    const loader = document.getElementById('login-loader');
    const errorMsg = document.getElementById('login-error');

    // UI Feedback: Loading
    btn.disabled = true;
    btnText.style.display = 'none';
    loader.style.display = 'block';
    errorMsg.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('parroquia_token', data.access_token);
            
            // Success animation or redirect
            window.location.href = 'index.html';
        } else {
            // Show error message
            errorMsg.style.display = 'flex';
            btn.disabled = false;
            btnText.style.display = 'block';
            loader.style.display = 'none';
        }
    } catch (error) {
        console.error("Login error:", error);
        alert("Error de conexión con el servidor.");
        btn.disabled = false;
        btnText.style.display = 'block';
        loader.style.display = 'none';
    }
});
