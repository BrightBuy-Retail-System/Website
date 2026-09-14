/**
 * api.js — Shared API Utility (Phase 1: Shared Foundation)
 * Standard fetch() wrappers for all 5 Flask Blueprints.
 * Each team member's blueprint uses these helpers to connect
 * to their /api/<module>/ endpoints.
 */

// ============================================================
// Base Configuration
// ============================================================

const API_BASE = window.location.origin;

const API_ENDPOINTS = {
    catalog:   `${API_BASE}/api/catalog`,
    authCart:  `${API_BASE}/api/auth-cart`,
    orders:    `${API_BASE}/api/orders`,
    logistics: `${API_BASE}/api/logistics`,
    analytics: `${API_BASE}/api/analytics`,
    health:    `${API_BASE}/api/health`,
};

// ============================================================
// Core Fetch Helpers
// ============================================================

/**
 * Generic GET request.
 * @param {string} url - Full URL to fetch.
 * @param {Object} [params] - URL query parameters as key-value pairs.
 * @returns {Promise<Object>} Parsed JSON response.
 */
async function apiGet(url, params = {}) {
    const queryString = new URLSearchParams(
        Object.fromEntries(Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== ''))
    ).toString();
    const fullUrl = queryString ? `${url}?${queryString}` : url;

    const response = await fetch(fullUrl, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
    return data;
}

/**
 * Generic POST request with JSON body.
 * @param {string} url - Full URL to post to.
 * @param {Object} body - Request body as JS object.
 * @returns {Promise<Object>} Parsed JSON response.
 */
async function apiPost(url, body = {}) {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(body),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
    return data;
}

/**
 * Generic PUT request with JSON body.
 * @param {string} url - Full URL to update.
 * @param {Object} body - Request body as JS object.
 * @returns {Promise<Object>} Parsed JSON response.
 */
async function apiPut(url, body = {}) {
    const response = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(body),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
    return data;
}

/**
 * Generic DELETE request.
 * @param {string} url - Full URL to delete.
 * @returns {Promise<Object>} Parsed JSON response.
 */
async function apiDelete(url) {
    const response = await fetch(url, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
    return data;
}

// ============================================================
// Module-specific Namespaced API helpers
// (Each blueprint member can extend their own namespace)
// ============================================================

/**
 * Catalog API — Member 1
 */
const CatalogAPI = {
    getCategories: ()        => apiGet(`${API_ENDPOINTS.catalog}/categories`),
    getProducts:   (params)  => apiGet(`${API_ENDPOINTS.catalog}/products`, params),
    getProduct:    (id)      => apiGet(`${API_ENDPOINTS.catalog}/products/${id}`),
    createProduct: (body)    => apiPost(`${API_ENDPOINTS.catalog}/products`, body),
    updateProduct: (id, body)=> apiPut(`${API_ENDPOINTS.catalog}/products/${id}`, body),
    deleteProduct: (id)      => apiDelete(`${API_ENDPOINTS.catalog}/products/${id}`),
};

/**
 * Auth & Cart API — Member 2
 */
const AuthCartAPI = {
    register:     (body)     => apiPost(`${API_ENDPOINTS.authCart}/register`, body),
    login:        (body)     => apiPost(`${API_ENDPOINTS.authCart}/login`, body),
    getCart:      (cid)      => apiGet(`${API_ENDPOINTS.authCart}/cart/${cid}`),
    addToCart:    (body)     => apiPost(`${API_ENDPOINTS.authCart}/cart`, body),
    updateCart:   (id, body) => apiPut(`${API_ENDPOINTS.authCart}/cart/${id}`, body),
    removeFromCart:(id)      => apiDelete(`${API_ENDPOINTS.authCart}/cart/${id}`),
};

/**
 * Orders API — Member 3
 */
const OrdersAPI = {
    getOrders:    (params)   => apiGet(`${API_ENDPOINTS.orders}/orders`, params),
    getOrder:     (id)       => apiGet(`${API_ENDPOINTS.orders}/orders/${id}`),
    createOrder:  (body)     => apiPost(`${API_ENDPOINTS.orders}/orders`, body),
    updateOrder:  (id, body) => apiPut(`${API_ENDPOINTS.orders}/orders/${id}`, body),
    cancelOrder:  (id)       => apiDelete(`${API_ENDPOINTS.orders}/orders/${id}`),
};

/**
 * Logistics API — Member 4
 */
const LogisticsAPI = {
    getShipments:   (params) => apiGet(`${API_ENDPOINTS.logistics}/shipments`, params),
    getShipment:    (id)     => apiGet(`${API_ENDPOINTS.logistics}/shipments/${id}`),
    createShipment: (body)   => apiPost(`${API_ENDPOINTS.logistics}/shipments`, body),
    updateShipment: (id,body)=> apiPut(`${API_ENDPOINTS.logistics}/shipments/${id}`, body),
};

/**
 * Analytics API — Member 5
 */
const AnalyticsAPI = {
    getSalesSummary: ()      => apiGet(`${API_ENDPOINTS.analytics}/sales-summary`),
    getTopProducts:  (limit) => apiGet(`${API_ENDPOINTS.analytics}/top-products`, { limit }),
    getCityBreakdown:()      => apiGet(`${API_ENDPOINTS.analytics}/city-breakdown`),
    getOrderTrends:  ()      => apiGet(`${API_ENDPOINTS.analytics}/order-trends`),
    getRevenueByCity:()      => apiGet(`${API_ENDPOINTS.analytics}/revenue-by-city`),
};

// ============================================================
// Toast Notification Utility
// ============================================================

/**
 * Show a toast notification in the bottom-right corner.
 * @param {string} message  - Toast body text.
 * @param {'success'|'danger'|'warning'|'info'} [type='info'] - Toast color type.
 * @param {number} [delay=3500] - Auto-hide delay in ms.
 */
function showToast(message, type = 'info', delay = 3500) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const iconMap = {
        success: 'bi-check-circle-fill',
        danger:  'bi-x-circle-fill',
        warning: 'bi-exclamation-triangle-fill',
        info:    'bi-info-circle-fill',
    };
    const colorMap = {
        success: '#34d399',
        danger:  '#f87171',
        warning: '#fbbf24',
        info:    '#60a5fa',
    };

    const id = `toast-${Date.now()}`;
    const icon = iconMap[type] || iconMap.info;
    const color = colorMap[type] || colorMap.info;

    const html = `
    <div id="${id}" class="toast align-items-center border-0 mb-2" role="alert" aria-live="assertive" style="
        background: var(--ls-bg-card);
        border: 1px solid var(--ls-border) !important;
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 13.5px;
        color: var(--ls-text-primary);
        min-width: 260px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.45);">
        <div class="d-flex align-items-center gap-2 p-3">
            <i class="bi ${icon}" style="color:${color}; font-size:16px; flex-shrink:0;"></i>
            <span class="flex-grow-1">${message}</span>
            <button type="button" class="btn-close btn-close-white btn-close-sm ms-2" data-bs-dismiss="toast"></button>
        </div>
    </div>`;

    container.insertAdjacentHTML('beforeend', html);
    const el = document.getElementById(id);
    const toast = new bootstrap.Toast(el, { delay });
    toast.show();
    el.addEventListener('hidden.bs.toast', () => el.remove());
}

// ============================================================
// Utility: Render Error State in a Container
// ============================================================

/**
 * Replace a container's content with a friendly error message.
 * @param {HTMLElement|string} container - DOM element or CSS selector.
 * @param {string} message - Error description.
 */
function renderError(container, message) {
    const el = typeof container === 'string' ? document.querySelector(container) : container;
    if (!el) return;
    el.innerHTML = `
        <div class="ls-empty-state">
            <div class="ls-empty-icon"><i class="bi bi-exclamation-triangle text-warning"></i></div>
            <p class="ls-empty-title">Something went wrong</p>
            <p class="ls-empty-desc">${message}</p>
        </div>`;
}

/**
 * Replace a container's content with an empty-state placeholder.
 * @param {HTMLElement|string} container - DOM element or CSS selector.
 * @param {string} [icon='bi-inbox'] - Bootstrap icon class.
 * @param {string} [title='No data found'] - Title text.
 * @param {string} [desc=''] - Description text.
 */
function renderEmpty(container, icon = 'bi-inbox', title = 'No data found', desc = '') {
    const el = typeof container === 'string' ? document.querySelector(container) : container;
    if (!el) return;
    el.innerHTML = `
        <div class="ls-empty-state">
            <div class="ls-empty-icon"><i class="bi ${icon}"></i></div>
            <p class="ls-empty-title">${title}</p>
            ${desc ? `<p class="ls-empty-desc">${desc}</p>` : ''}
        </div>`;
}

/**
 * Escape HTML to prevent XSS.
 * @param {string} str
 * @returns {string}
 */
function escHtml(str) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(str ?? ''));
    return div.innerHTML;
}

/**
 * Format a price number as USD currency string.
 * @param {number} value
 * @returns {string}
 */
function fmtCurrency(value) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value ?? 0);
}

/**
 * Format an ISO date string to a readable local date.
 * @param {string} dateStr
 * @returns {string}
 */
function fmtDate(dateStr) {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}
