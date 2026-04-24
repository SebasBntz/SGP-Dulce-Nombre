const API_BASE = '/api/v1';

window.addEventListener('load', () => {
    // If already logged in, go to dashboard
    if (sessionStorage.getItem('parroquia_token')) {
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
            sessionStorage.setItem('parroquia_token', data.access_token);
            
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

// --- View Toggling Logic ---
const viewLogin = document.getElementById('view-login');
const viewForgot = document.getElementById('view-forgot');
const viewReset = document.getElementById('view-reset');

document.getElementById('link-forgot-password').addEventListener('click', (e) => {
    e.preventDefault();
    viewLogin.style.display = 'none';
    viewForgot.style.display = 'block';
});

document.getElementById('link-back-login').addEventListener('click', (e) => {
    e.preventDefault();
    viewForgot.style.display = 'none';
    viewLogin.style.display = 'block';
});

document.getElementById('link-back-login-2').addEventListener('click', (e) => {
    e.preventDefault();
    viewReset.style.display = 'none';
    viewLogin.style.display = 'block';
});

// --- Forgot Password Logic ---
let resetEmail = "";

document.getElementById('forgot-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    resetEmail = document.getElementById('forgot-email').value;
    const btn = document.getElementById('btn-forgot');
    const text = document.getElementById('btn-forgot-text');
    
    btn.disabled = true;
    text.innerText = "Enviando...";

    try {
        const response = await fetch(`${API_BASE}/auth/forgot-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: resetEmail })
        });
        
        // Go to reset UI regardless of response status to prevent email enumeration
        viewForgot.style.display = 'none';
        viewReset.style.display = 'block';
    } catch (err) {
        alert("Error de conexión al servidor");
    } finally {
        btn.disabled = false;
        text.innerText = "Enviar PIN";
    }
});

// --- Reset Password Logic ---
document.getElementById('reset-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const pin = document.getElementById('reset-pin').value;
    const newPassword = document.getElementById('reset-password').value;
    const btn = document.getElementById('btn-reset');
    const text = document.getElementById('btn-reset-text');
    const errorDiv = document.getElementById('reset-error');
    const errorText = document.getElementById('reset-error-text');

    // Limpiar error anterior
    errorDiv.style.display = 'none';

    btn.disabled = true;
    text.innerText = "Cambiando...";

    try {
        const response = await fetch(`${API_BASE}/auth/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                email: resetEmail,
                token: pin,
                new_password: newPassword
            })
        });

        if (response.ok) {
            // Éxito: volver al login con mensaje
            viewReset.style.display = 'none';
            viewLogin.style.display = 'block';
            document.getElementById('login-email').value = resetEmail;
            document.getElementById('login-password').value = "";
            document.getElementById('login-password').focus();
            
            // Mostrar éxito en el login-error con color verde temporal
            const loginError = document.getElementById('login-error');
            const loginErrorText = document.getElementById('login-error-text');
            loginError.style.display = 'flex';
            loginError.style.background = '#dcfce7';
            loginError.style.color = '#16a34a';
            loginError.style.borderColor = '#bbf7d0';
            loginErrorText.innerText = '✓ Contraseña cambiada exitosamente. Ya puedes iniciar sesión.';
            setTimeout(() => { loginError.style.display = 'none'; }, 5000);
        } else {
            const errData = await response.json().catch(() => ({}));
            // Mostrar error inline — sin alert() para evitar bugs de foco en Electron
            errorText.innerText = errData.detail || "PIN inválido o expirado. Intenta nuevamente.";
            errorDiv.style.display = 'flex';
            // Limpiar solo el PIN para que el usuario reintente
            const pinField = document.getElementById('reset-pin');
            pinField.value = '';
            pinField.focus();
        }
    } catch (err) {
        errorText.innerText = "Error de conexión al servidor.";
        errorDiv.style.display = 'flex';
        const pinField = document.getElementById('reset-pin');
        pinField.value = '';
        pinField.focus();
    } finally {
        btn.disabled = false;
        text.innerText = "Cambiar Contraseña";
    }
});
