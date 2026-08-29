/**
 * auth.js — JWT session handling + page-guard for KrishiMitra.
 * Include on every page (login.html, register.html, index.html).
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
        window.location.href = 'login.html';
    },
    // Call at the top of any page that requires login (e.g. index.html).
    // Redirects to login.html if there's no token.
    requireAuth() {
        if (!this.isLoggedIn()) {
            window.location.href = 'login.html';
        }
    },
    // Call at the top of login.html / register.html.
    // If already logged in, skip straight to the app.
    redirectIfLoggedIn() {
        if (this.isLoggedIn()) {
            window.location.href = 'index.html';
        }
    },
};
window.Auth = Auth;