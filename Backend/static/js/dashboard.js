/**
 * dashboard.js — Shared Dashboard Interactivity (Phase 1)
 * Sidebar toggle, health check polling, active nav highlighting.
 */

// ============================================================
// Sidebar Toggle (Mobile)
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    const sidebar   = document.getElementById('sidebar');
    const toggle    = document.getElementById('sidebarToggle');
    const main      = document.getElementById('mainContent');

    if (toggle && sidebar) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth < 992 &&
                sidebar.classList.contains('open') &&
                !sidebar.contains(e.target) &&
                !toggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        });
    }

    // Initialize tooltips
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
        new bootstrap.Tooltip(el);
    });

    // Run initial health check
    refreshHealth();
});

// ============================================================
// DB Health Check
// ============================================================

/**
 * Fetch /api/health and update the navbar health badge.
 */
async function refreshHealth() {
    const badge = document.getElementById('navHealthBadge');
    if (!badge) return;

    const dot   = badge.querySelector('.ls-health-dot');
    const label = badge.querySelector('.ls-health-label');

    label.textContent = 'Checking...';
    dot.className = 'ls-health-dot';

    try {
        const data = await apiGet(`${API_BASE}/api/health`);
        if (data.database && data.database.status === 'healthy') {
            dot.classList.add('healthy');
            label.textContent = `DB: ${data.database.database}`;
        } else {
            dot.classList.add('unhealthy');
            label.textContent = 'DB Offline';
        }
    } catch (err) {
        dot.classList.add('unhealthy');
        label.textContent = 'DB Error';
    }
}

// ============================================================
// Generic Table Loader Helper
// ============================================================

/**
 * Show a loading skeleton inside a table body.
 * @param {string} tbodyId - ID of the <tbody> element.
 * @param {number} cols - Number of columns.
 * @param {number} [rows=5] - Number of skeleton rows.
 */
function showTableSkeleton(tbodyId, cols, rows = 5) {
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;
    tbody.innerHTML = Array.from({ length: rows }, () => `
        <tr>
            ${Array.from({ length: cols }, () =>
                `<td><div class="ls-skeleton" style="height:18px; border-radius:4px;"></div></td>`
            ).join('')}
        </tr>`).join('');
}

/**
 * Show "no data" state inside a table body.
 * @param {string} tbodyId
 * @param {number} cols
 * @param {string} [msg='No records found']
 */
function showTableEmpty(tbodyId, cols, msg = 'No records found') {
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;
    tbody.innerHTML = `
        <tr>
            <td colspan="${cols}" class="text-center py-5">
                <div class="ls-empty-state" style="padding: 30px 20px;">
                    <div class="ls-empty-icon"><i class="bi bi-inbox"></i></div>
                    <p class="ls-empty-title">${msg}</p>
                </div>
            </td>
        </tr>`;
}
