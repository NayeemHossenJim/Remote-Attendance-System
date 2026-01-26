const API_BASE = window.location.origin + '/api';
let currentUser = null;
let authToken = localStorage.getItem('authToken');

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    if (authToken) {
        initApp();
    } else {
        showAuth('login');
    }
});

// --- Navigation & View Management ---
function showAuth(view) {
    document.getElementById('app-layout').classList.add('hidden');
    document.getElementById('auth-layout').classList.remove('hidden');

    document.querySelectorAll('.auth-view').forEach(el => el.classList.add('hidden'));
    document.getElementById(`${view}-view`).classList.remove('hidden');
}

async function initApp() {
    document.getElementById('auth-layout').classList.add('hidden');
    document.getElementById('app-layout').classList.remove('hidden');

    await loadUserInfo();
    showSection('checkin');
}

function showSection(sectionId) {
    // Update Sidebar Active State
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.section === sectionId) link.classList.add('active');
    });

    // Validations for role-based access
    if (sectionId === 'approvals' && !['team_lead', 'admin'].includes(currentUser.role)) return;
    if (sectionId === 'employees' && currentUser.role !== 'admin') return;

    // Show Content
    document.querySelectorAll('.content-section').forEach(el => el.classList.add('hidden'));
    const target = document.getElementById(`${sectionId}-section`);
    if (target) target.classList.remove('hidden');

    // Load Data
    if (sectionId === 'checkin') setupCheckinView();
    if (sectionId === 'history') loadHistory();
    if (sectionId === 'approvals') loadPendingApprovals();
    if (sectionId === 'employees') loadEmployees();
}

function logout() {
    localStorage.removeItem('authToken');
    authToken = null;
    currentUser = null;
    showAuth('login');
}

// --- Data Loading ---
async function loadUserInfo() {
    try {
        const res = await fetchWithAuth('/auth/me');
        if (res.ok) {
            currentUser = await res.json();
            renderSidebarProfile();
            updateSidebarPermissions();
        } else {
            logout();
        }
    } catch (e) {
        console.error("Auth validation failed", e);
        logout();
    }
}

function renderSidebarProfile() {
    const container = document.getElementById('sidebar-user-info');
    if (container) {
        container.innerHTML = `
            <strong>${currentUser.office_id}</strong>
            <span style="opacity: 0.7; font-size: 11px;">${currentUser.role.toUpperCase()}</span>
        `;
    }
}

function updateSidebarPermissions() {
    const approvalLink = document.querySelector('[data-section="approvals"]');
    const employeeLink = document.querySelector('[data-section="employees"]');

    if (currentUser.role === 'team_lead' || currentUser.role === 'admin') {
        approvalLink.classList.remove('hidden');
    }
    if (currentUser.role === 'admin') {
        employeeLink.classList.remove('hidden');
    }
}

// --- Features ---

/* CHECK-IN */
function setupCheckinView() {
    // Reset view state
    document.getElementById('checkin-result').innerHTML = '';
    document.getElementById('late-request-form').classList.add('hidden');
    document.getElementById('checkin-btn').disabled = false;
}

async function performCheckIn() {
    const btn = document.getElementById('checkin-btn');
    btn.disabled = true;
    showToast('Getting location...', 'info');

    try {
        const pos = await getGeoLocation();
        const res = await fetchWithAuth('/attendance/check-in', 'POST', {
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude
        });
        const data = await res.json();

        if (res.ok) {
            renderCheckinResult(data);
        } else {
            showToast(data.detail || 'Check-in failed', 'error');
        }
    } catch (e) {
        showToast(e.message, 'error');
    } finally {
        btn.disabled = false;
    }
}

function renderCheckinResult(data) {
    const resultDiv = document.getElementById('checkin-result');
    const type = data.status === 'PRESENT' ? 'success' : 'error';

    resultDiv.innerHTML = `
        <div class="alert alert-${type}">
            <strong>${data.status}</strong>: ${data.message}
            <br><small>Distance: ${data.distance_from_home ? data.distance_from_home.toFixed(0) + 'm' : 'Unknown'}</small>
        </div>
    `;

    if (data.can_request_present) {
        document.getElementById('late-request-form').classList.remove('hidden');
    }
}

async function submitLateRequest() {
    const reason = document.getElementById('late-reason').value;
    if (!reason) return showToast('Please enter a reason', 'error');

    showToast('Submitting...', 'info');
    try {
        const pos = await getGeoLocation();
        const res = await fetchWithAuth('/attendance/late-check-in-request', 'POST', {
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
            reason: reason
        });

        if (res.ok) {
            showToast('Request submitted successfully', 'success');
            document.getElementById('late-request-form').classList.add('hidden');
        } else {
            const data = await res.json();
            showToast(data.detail, 'error');
        }
    } catch (e) {
        showToast(e.message, 'error');
    }
}

/* HISTORY */
async function loadHistory() {
    const container = document.getElementById('history-list');
    container.innerHTML = '<div class="spinner" style="margin: 20px auto;"></div>';

    const res = await fetchWithAuth('/attendance/history');
    if (res.ok) {
        const records = await res.json();
        container.innerHTML = records.length ? records.map(renderAttendanceItem).join('') : '<p class="text-center">No records found.</p>';
    }
}

/* APPROVALS */
async function loadPendingApprovals() {
    const container = document.getElementById('approvals-list');
    container.innerHTML = '<div class="spinner" style="margin: 20px auto;"></div>';

    const res = await fetchWithAuth('/attendance/pending-approvals');
    if (res.ok) {
        const records = await res.json();
        container.innerHTML = records.length ? records.map(renderApprovalItem).join('') : '<p class="text-center">No pending approvals.</p>';
    }
}

async function handleApproval(id, approve) {
    const comment = approve ? null : prompt("Rejection reason (optional):");
    try {
        const res = await fetchWithAuth('/attendance/approve-request', 'POST', {
            attendance_id: id,
            approve: approve,
            comment: comment
        });
        if (res.ok) {
            showToast(`Request ${approve ? 'Approved' : 'Rejected'}`, 'success');
            loadPendingApprovals();
        }
    } catch (e) {
        showToast('Action failed', 'error');
    }
}

/* EMPLOYEES */
async function loadEmployees() {
    const container = document.getElementById('employees-list');
    container.innerHTML = '<div class="spinner" style="margin: 20px auto;"></div>';

    const res = await fetchWithAuth('/auth/users');
    if (res.ok) {
        const users = await res.json();
        container.innerHTML = users.map(u => `
            <div class="list-item">
                <div>
                    <div style="font-weight: 600">${u.office_id}</div>
                    <div style="font-size: 13px; color: var(--secondary)">${u.role}</div>
                </div>
                <div style="text-align: right; font-size: 13px;">
                    <div>${u.home_latitude ? 'Location Set' : 'No Location'}</div>
                </div>
            </div>
        `).join('');
    }
}

/* HELPERS */
function renderAttendanceItem(record) {
    const date = new Date(record.created_at).toLocaleString();
    let statusClass = 'badge-pending';
    if (record.status === 'PRESENT') statusClass = 'badge-present';
    if (record.status === 'ABSENT') statusClass = 'badge-absent';

    return `
        <div class="list-item">
            <div>
                <div style="font-weight: 500">${date}</div>
                <div style="font-size: 13px; color: var(--secondary)">
                    ${record.distance_from_home ? `${record.distance_from_home.toFixed(0)}m away` : ''} 
                    ${record.is_late_request ? '(Late Request)' : ''}
                </div>
            </div>
            <span class="badge ${statusClass}">${record.status}</span>
        </div>
    `;
}

function renderApprovalItem(record) {
    return `
        <div class="card">
            <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                <strong>User ID: ${record.user_id}</strong>
                <span style="font-size: 12px; color: var(--secondary)">${new Date(record.created_at).toLocaleTimeString()}</span>
            </div>
            <p style="font-size: 14px; margin-bottom: 12px;">Reason: "${record.late_request_reason}"</p>
            <div style="display: flex; gap: 8px;">
                <button class="btn btn-success" style="flex: 1" onclick="handleApproval(${record.id}, true)">Approve</button>
                <button class="btn btn-danger" style="flex: 1" onclick="handleApproval(${record.id}, false)">Reject</button>
            </div>
        </div>
    `;
}

async function fetchWithAuth(endpoint, method = 'GET', body = null) {
    const opts = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        }
    };
    if (body) opts.body = JSON.stringify(body);
    return fetch(API_BASE + endpoint, opts);
}

function getGeoLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) reject(new Error("Geolocation not supported"));
        navigator.geolocation.getCurrentPosition(resolve, reject);
    });
}

function showToast(msg, type = 'info') {
    // Simple alert implementation for now, can be upgraded to real toast
    // Ideally we append a div to body and remove it after 3s
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Handling Login/Register Forms directly
let regLoc = null;

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const officeId = document.getElementById('login-id').value;
    const pass = document.getElementById('login-pass').value;

    try {
        const res = await fetch(API_BASE + '/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ office_id: officeId, password: pass })
        });
        const data = await res.json();
        if (res.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            initApp();
        } else {
            showToast(data.detail, 'error');
        }
    } catch (e) {
        showToast('Login failed', 'error');
    }
});

// Registration Logic
async function captureRegLocation() {
    const btn = document.getElementById('get-loc-btn');
    const status = document.getElementById('reg-loc-status');
    btn.disabled = true;
    status.textContent = "Locating...";

    try {
        const pos = await getGeoLocation();
        regLoc = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        status.textContent = `${regLoc.lat.toFixed(4)}, ${regLoc.lng.toFixed(4)}`;
        status.style.color = "var(--success-text)";
        document.getElementById('reg-submit-btn').disabled = false;
        showToast("Location captured", "success");
    } catch (e) {
        status.textContent = "Failed to get location";
        status.style.color = "var(--error-text)";
        showToast("Location capture failed", "error");
    } finally {
        btn.disabled = false;
    }
}
// Expose function to global scope for onclick handler
window.captureRegLocation = captureRegLocation;

document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!regLoc) return showToast("Location required", "error");

    const payload = {
        office_id: document.getElementById('reg-id').value,
        password: document.getElementById('reg-pass').value,
        email: document.getElementById('reg-email').value,
        latitude: regLoc.lat,
        longitude: regLoc.lng
    };

    try {
        const res = await fetch(API_BASE + '/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
            showToast("Registration successful", "success");
            showAuth('login');
        } else {
            showToast(data.detail || "Registration failed", "error");
        }
    } catch (e) {
        showToast("Error registering", "error");
    }
});
