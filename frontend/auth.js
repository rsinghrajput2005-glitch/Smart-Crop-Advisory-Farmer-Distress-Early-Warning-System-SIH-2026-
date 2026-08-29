/**
 * auth.js — Login / 3-step signup + JWT session handling for KrishiMitra.
 * Loaded before app.js. Exposes window.Auth for app.js to use.
 */

const AUTH_API_BASE = 'http://localhost:8000';
const TOKEN_KEY = 'krishimitra_token';

const Auth = {
    getToken() {
        return localStorage.getItem(TOKEN_KEY);
    },
    setToken(token) {
        localStorage.setItem(TOKEN_KEY, token);
    },
    clearToken() {
        localStorage.removeItem(TOKEN_KEY);
    },
    isLoggedIn() {
        return !!this.getToken();
    },
    authHeader() {
        const token = this.getToken();
        return token ? { Authorization: `Bearer ${token}` } : {};
    },
    logout() {
        this.clearToken();
        window.location.reload();
    },
};
window.Auth = Auth;

// ── Modal rendering ──────────────────────────────────────────────────────
let signupStep = 'email'; // email -> otp -> details
let signupEmail = '';

function renderAuthModal() {
    const existing = document.getElementById('auth-overlay');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.id = 'auth-overlay';
    overlay.className = 'auth-overlay';
    overlay.innerHTML = `
      <div class="auth-card">
        <div class="auth-brand">🌱 KrishiMitra</div>
        <div class="auth-tabs">
          <button class="auth-tab active" id="tab-login">Login</button>
          <button class="auth-tab" id="tab-signup">Sign up</button>
        </div>
        <div id="auth-body"></div>
        <div class="auth-error hidden" id="auth-error"></div>
      </div>
    `;
    document.body.appendChild(overlay);

    document.getElementById('tab-login').addEventListener('click', () => showLoginForm());
    document.getElementById('tab-signup').addEventListener('click', () => {
        signupStep = 'email';
        showSignupForm();
    });

    showLoginForm();
}

function setAuthTab(active) {
    document.getElementById('tab-login').classList.toggle('active', active === 'login');
    document.getElementById('tab-signup').classList.toggle('active', active === 'signup');
}

function showAuthError(msg) {
    const el = document.getElementById('auth-error');
    el.textContent = msg;
    el.classList.remove('hidden');
}
function clearAuthError() {
    const el = document.getElementById('auth-error');
    el.textContent = '';
    el.classList.add('hidden');
}

function showLoginForm() {
    setAuthTab('login');
    clearAuthError();
    document.getElementById('auth-body').innerHTML = `
      <form id="login-form" class="auth-form">
        <label>Email</label>
        <input type="email" id="login-email" required>
        <label>Password</label>
        <input type="password" id="login-password" required>
        <button type="submit" class="btn-primary">Log in</button>
      </form>
    `;
    document.getElementById('login-form').addEventListener('submit', async e => {
        e.preventDefault();
        clearAuthError();
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value;
        try {
            const res = await fetch(`${AUTH_API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Login failed');
            Auth.setToken(data.access_token);
            document.getElementById('auth-overlay').remove();
            if (window.onAuthReady) window.onAuthReady();
        } catch (err) {
            showAuthError(err.message);
        }
    });
}

function showSignupForm() {
    setAuthTab('signup');
    clearAuthError();
    const body = document.getElementById('auth-body');

    if (signupStep === 'email') {
        body.innerHTML = `
          <form id="signup-email-form" class="auth-form">
            <label>Email</label>
            <input type="email" id="signup-email" required>
            <button type="submit" class="btn-primary">Send OTP</button>
          </form>
        `;
        document.getElementById('signup-email-form').addEventListener('submit', async e => {
            e.preventDefault();
            clearAuthError();
            const email = document.getElementById('signup-email').value.trim();
            try {
                const res = await fetch(`${AUTH_API_BASE}/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email }),
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Could not send OTP');
                signupEmail = email;
                signupStep = 'otp';
                showSignupForm();
            } catch (err) {
                showAuthError(err.message);
            }
        });
    } else if (signupStep === 'otp') {
        body.innerHTML = `
          <p class="auth-hint">OTP sent to <strong>${signupEmail}</strong></p>
          <form id="signup-otp-form" class="auth-form">
            <label>Enter OTP</label>
            <input type="text" id="signup-otp" required maxlength="6">
            <button type="submit" class="btn-primary">Verify</button>
          </form>
        `;
        document.getElementById('signup-otp-form').addEventListener('submit', async e => {
            e.preventDefault();
            clearAuthError();
            const otp = document.getElementById('signup-otp').value.trim();
            try {
                const res = await fetch(`${AUTH_API_BASE}/auth/verify-otp`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: signupEmail, otp }),
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Invalid OTP');
                signupStep = 'details';
                showSignupForm();
            } catch (err) {
                showAuthError(err.message);
            }
        });
    } else if (signupStep === 'details') {
        body.innerHTML = `
          <form id="signup-details-form" class="auth-form">
            <label>Username</label>
            <input type="text" id="signup-username" required>
            <label>Password</label>
            <input type="password" id="signup-password" required minlength="6">
            <button type="submit" class="btn-primary">Create account</button>
          </form>
        `;
        document.getElementById('signup-details-form').addEventListener('submit', async e => {
            e.preventDefault();
            clearAuthError();
            const username = document.getElementById('signup-username').value.trim();
            const password = document.getElementById('signup-password').value;
            try {
                const res = await fetch(`${AUTH_API_BASE}/auth/complete-registration`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: signupEmail, username, password }),
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Registration failed');
                // Auto-login after successful signup
                const loginRes = await fetch(`${AUTH_API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: signupEmail, password }),
                });
                const loginData = await loginRes.json();
                if (!loginRes.ok) throw new Error('Account created — please log in.');
                Auth.setToken(loginData.access_token);
                document.getElementById('auth-overlay').remove();
                if (window.onAuthReady) window.onAuthReady();
            } catch (err) {
                showAuthError(err.message);
            }
        });
    }
}

// Entry point: call this from app.js once DOM is ready.
function initAuthGate(onReady) {
    window.onAuthReady = onReady;
    if (Auth.isLoggedIn()) {
        onReady();
    } else {
        renderAuthModal();
    }
}
window.initAuthGate = initAuthGate;