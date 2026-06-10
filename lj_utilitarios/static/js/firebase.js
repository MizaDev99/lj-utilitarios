import { initializeApp }
    from 'https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut }
    from 'https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js';

/* ── Ler config do elemento <div id="firebase-config"> ── */
function getFirebaseConfig() {
    const el = document.getElementById('firebase-config');
    if (!el) return null;
    const cfg = {
        apiKey:            el.dataset.apiKey,
        authDomain:        el.dataset.authDomain,
        projectId:         el.dataset.projectId,
        storageBucket:     el.dataset.storageBucket,
        messagingSenderId: el.dataset.messagingSenderId,
        appId:             el.dataset.appId,
    };
    return cfg.apiKey ? cfg : null;
}

function getCsrf() {
    return document.cookie.match(/csrftoken=([^;]+)/)?.[1]
        || window.CSRF_TOKEN
        || '';
}

/* ── Toast de feedback ── */
function mostrarToast(msg, tipo = 'info') {
    const toast = document.getElementById('toast-login');
    if (!toast) return;
    toast.textContent = msg;
    toast.style.background = tipo === 'erro'
        ? 'rgba(239,68,68,0.95)'
        : 'rgba(124,58,237,0.95)';
    toast.style.display = 'flex';
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => { toast.style.display = 'none'; }, 4000);
}

/* ── Inicializar Firebase ── */
const config = getFirebaseConfig();
let auth     = null;
let provider = null;

if (config) {
    try {
        const app = initializeApp(config);
        auth       = getAuth(app);
        provider   = new GoogleAuthProvider();
        provider.addScope('email');
        provider.addScope('profile');
    } catch (e) {
        console.error('[Firebase] Erro na inicialização:', e);
    }
}

/* ── Login com Google ── */
async function loginComGoogle(nextUrl = '/') {
    if (!auth) {
        mostrarToast('Firebase não configurado no servidor.', 'erro');
        return;
    }
    try {
        const result  = await signInWithPopup(auth, provider);
        const idToken = await result.user.getIdToken();

        const res  = await fetch('/auth/google/', {
            method:  'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken':  getCsrf(),
            },
            body: JSON.stringify({ id_token: idToken }),
        });
        const data = await res.json();

        if (data.success) {
            mostrarToast('Login realizado! Redirecionando...');
            setTimeout(() => { window.location.href = nextUrl; }, 800);
        } else {
            mostrarToast('Erro no login: ' + (data.error || 'tente novamente'), 'erro');
        }

    } catch (err) {
        if (err.code === 'auth/popup-blocked') {
            mostrarToast('Popup bloqueado! Permita popups para este site.', 'erro');
        } else if (
            err.code !== 'auth/popup-closed-by-user' &&
            err.code !== 'auth/cancelled-popup-request'
        ) {
            console.error('[Firebase] Erro no login:', err);
            mostrarToast('Erro ao conectar com Google.', 'erro');
        }
    }
}

/* ── Logout ── */
async function fazerLogout() {
    if (auth) {
        try { await signOut(auth); } catch (_) {}
    }
    await fetch('/auth/logout/', {
        method:  'POST',
        headers: { 'X-CSRFToken': getCsrf() },
    }).catch(() => {});
    window.location.href = '/';
}

/* ── Event listeners (DOMContentLoaded) ── */
document.addEventListener('DOMContentLoaded', () => {

    /* Botões de login — qualquer elemento com [data-google-login] */
    document.querySelectorAll('[data-google-login]').forEach(btn => {
        btn.addEventListener('click', () => {
            loginComGoogle(btn.dataset.next || '/');
        });
    });

    /* Botões de logout */
    document.querySelectorAll('#btn-logout, .btn-logout').forEach(btn => {
        btn.addEventListener('click', fazerLogout);
    });

    /* Toast automático quando redirecionado por falta de login */
    const params = new URLSearchParams(window.location.search);
    if (params.get('login_required') === 'true') {
        mostrarToast('Faça login com Google para finalizar sua compra. 🔐');
    }
});

/* ── Globais (compatibilidade com onclick inline legado) ── */
window.handleGoogleLogin = () => loginComGoogle('/');
window.handleLogout      = fazerLogout;
