// ═══════════════════════════════════════════════════════════
// AI SHOP — MAIN JAVASCRIPT FILE
// Complete interactive functionality for AI-powered e-commerce
// ═══════════════════════════════════════════════════════════

// ═══════════════════════════════════════════════════════════
// 1. CSRF TOKEN HELPERS
// ═══════════════════════════════════════════════════════════

/**
 * Get CSRF token from form input
 */
function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : null;
}

/**
 * Get CSRF token from cookie (fallback)
 */
function getCookieCsrf() {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; csrftoken=`);
    if (parts.length === 2) {
        return parts.pop().split(';').shift();
    }
    return null;
}

// ═══════════════════════════════════════════════════════════
// 2. ADD TO CART (AJAX)
// ═══════════════════════════════════════════════════════════

/**
 * Add product to cart via AJAX
 * @param {number} productId - Product ID to add
 */
function addToCart(productId, quantity = 1, triggerButton = null) {
    const parsedQuantity = Number.parseInt(quantity, 10);
    const safeQuantity = Number.isFinite(parsedQuantity) && parsedQuantity > 0 ? parsedQuantity : 1;
    if (triggerButton) {
        triggerButton.disabled = true;
        triggerButton.classList.add('btn-loading');
    }

    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken() || getCookieCsrf(),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quantity: safeQuantity })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast(data.message, 'success');
                updateCartBadge(data.cart_count);

                // Animate cart icon
                const cartIcon = document.getElementById('cart-count-badge');
                if (cartIcon) {
                    cartIcon.classList.add('bounce');
                    setTimeout(() => cartIcon.classList.remove('bounce'), 500);
                }
            } else {
                const msg = data.message || 'Error adding to cart';
                const type = msg.toLowerCase().includes('stock') ? 'warning' : 'error';
                showToast(msg, type);
            }
        })
        .catch(error => {
            console.error('Cart error:', error);
            showToast('Network error. Please try again.', 'error');
        })
        .finally(() => {
            if (triggerButton) {
                triggerButton.disabled = false;
                triggerButton.classList.remove('btn-loading');
            }
        });
}

// ═══════════════════════════════════════════════════════════
// 3. TOAST NOTIFICATIONS
// ═══════════════════════════════════════════════════════════

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type: success, error, warning, info
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container') || createToastContainer();

    const toast = document.createElement('div');

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    const colors = {
        success: 'bg-success',
        error: 'bg-danger',
        warning: 'bg-warning',
        info: 'bg-info'
    };

    toast.className = `toast show ${colors[type]} text-white border-0 mb-2`;
    toast.style.cssText = 'min-width: 300px; max-width: 400px; animation: slideInRight 0.3s ease;';

    toast.innerHTML = `
        <div class="toast-body d-flex align-items-center">
            <span class="me-2">${icons[type]}</span>
            <span>${message}</span>
            <button type="button" class="btn-close btn-close-white ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;

    container.appendChild(toast);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 4000);
}

/**
 * Create toast container if it doesn't exist
 */
function createToastContainer() {
    const div = document.createElement('div');
    div.id = 'toast-container';
    div.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999;';
    document.body.appendChild(div);
    return div;
}

// ═══════════════════════════════════════════════════════════
// 4. UPDATE CART BADGE
// ═══════════════════════════════════════════════════════════

/**
 * Update cart badge count
 * @param {number} count - Number of items in cart
 */
function updateCartBadge(count) {
    const badges = document.querySelectorAll('.cart-badge, .cart-count-badge');
    badges.forEach(badge => {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    });
}

// ═══════════════════════════════════════════════════════════
// 5. COUNTDOWN TIMER
// ═══════════════════════════════════════════════════════════

/**
 * Start countdown timer
 * @param {number} targetHours - Hours to count down from
 */
function startCountdown(targetHours = 24) {
    const endTime = new Date(Date.now() + targetHours * 60 * 60 * 1000);

    function update() {
        const now = new Date();
        const diff = endTime - now;

        if (diff <= 0) {
            clearInterval(timer);
            return;
        }

        const hours = Math.floor(diff / 3600000).toString().padStart(2, '0');
        const minutes = Math.floor((diff % 3600000) / 60000).toString().padStart(2, '0');
        const seconds = Math.floor((diff % 60000) / 1000).toString().padStart(2, '0');

        const element = document.getElementById('countdown');
        if (element) {
            element.innerHTML = `<i class="fas fa-clock me-2 text-danger"></i>${hours}:${minutes}:${seconds}`;
        }
    }

    const timer = setInterval(update, 1000);
    update(); // Initial call
}

// ═══════════════════════════════════════════════════════════
// 6. STAR RATING WIDGET
// ═══════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    const stars = document.querySelectorAll('.rating-star');

    stars.forEach(star => {
        // Hover effect
        star.addEventListener('mouseover', () => {
            const value = star.dataset.value;
            stars.forEach(s => {
                if (s.dataset.value <= value) {
                    s.classList.remove('far');
                    s.classList.add('fas');
                } else {
                    s.classList.remove('fas');
                    s.classList.add('far');
                }
            });
        });

        // Click to select rating
        star.addEventListener('click', () => {
            const value = star.dataset.value;
            const ratingInput = document.getElementById('rating-input');
            if (ratingInput) {
                ratingInput.value = value;
            }

            stars.forEach(s => {
                if (s.dataset.value <= value) {
                    s.classList.remove('far');
                    s.classList.add('fas');
                    s.style.color = '#FFD700';
                } else {
                    s.classList.remove('fas');
                    s.classList.add('far');
                    s.style.color = '#dee2e6';
                }
            });
        });
    });

    // Reset on mouse leave
    const ratingContainer = document.querySelector('.rating-stars');
    if (ratingContainer) {
        ratingContainer.addEventListener('mouseleave', () => {
            const ratingInput = document.getElementById('rating-input');
            const currentValue = ratingInput ? ratingInput.value : 0;

            stars.forEach(s => {
                if (s.dataset.value <= currentValue) {
                    s.classList.remove('far');
                    s.classList.add('fas');
                    s.style.color = '#FFD700';
                } else {
                    s.classList.remove('fas');
                    s.classList.add('far');
                    s.style.color = '#dee2e6';
                }
            });
        });
    }
});

// ═══════════════════════════════════════════════════════════
// 7. IMAGE PREVIEW (for upload forms)
// ═══════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    const imageInput = document.getElementById('image-input');

    if (imageInput) {
        imageInput.addEventListener('change', function () {
            const file = this.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                const preview = document.getElementById('image-preview');
                if (preview) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                }
            };
            reader.readAsDataURL(file);
        });
    }
});

// ═══════════════════════════════════════════════════════════
// 8. NAVBAR SCROLL EFFECT (Amazon-Style Sticky)
// ═══════════════════════════════════════════════════════════

window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar-top');
    const subbar = document.querySelector('.navbar-subbar');

    if (navbar) {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }
});

// ═══════════════════════════════════════════════════════════
// 9. AUTO-DISMISS MESSAGES
// ═══════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            } else {
                alert.remove();
            }
        });
    }, 4000);
});

// ═══════════════════════════════════════════════════════════
// 10. REFRESH RECOMMENDATIONS (AJAX)
// ═══════════════════════════════════════════════════════════

/**
 * Refresh AI recommendations
 */
function refreshRecs() {
    const btn = document.getElementById('refresh-btn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Analyzing...';
    }

    fetch('/recommendations/refresh/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken() || getCookieCsrf(),
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            showToast(data.message, 'success');
            setTimeout(() => location.reload(), 1500);
        })
        .catch(error => {
            console.error('Refresh error:', error);
            showToast('Error refreshing. Please try again.', 'error');
        })
        .finally(() => {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-sync-alt me-1"></i> Refresh';
            }
        });
}

/**
 * Alternative function name for recommendations refresh
 */
function refreshRecommendations() {
    refreshRecs();
}

// ═══════════════════════════════════════════════════════════
// 11. PASSWORD STRENGTH INDICATOR
// ═══════════════════════════════════════════════════════════

/**
 * Calculate password strength
 * @param {string} password - Password to evaluate
 * @returns {object} Strength details
 */
function getPasswordStrength(password) {
    let score = 0;

    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;

    const levels = [
        { percent: 25, color: 'danger', label: 'Weak' },
        { percent: 50, color: 'warning', label: 'Fair' },
        { percent: 75, color: 'info', label: 'Good' },
        { percent: 100, color: 'success', label: 'Strong' }
    ];

    return levels[Math.max(0, score - 1)] || levels[0];
}

// Initialize password strength indicator
document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('id_password1');

    if (passwordInput) {
        passwordInput.addEventListener('input', function () {
            const strength = getPasswordStrength(this.value);
            const bar = document.getElementById('password-strength-bar');
            const label = document.getElementById('password-strength-label');

            if (bar) {
                bar.style.width = strength.percent + '%';
                bar.className = `progress-bar bg-${strength.color}`;
            }

            if (label) {
                label.textContent = strength.label;
                label.className = `text-${strength.color}`;
            }
        });
    }
});

// ═══════════════════════════════════════════════════════════
// 12. ADDITIONAL ANIMATIONS & EFFECTS
// ═══════════════════════════════════════════════════════════

// Add bounce animation CSS dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes bounce {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.2); }
    }
    
    .bounce {
        animation: bounce 0.5s ease;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// ═══════════════════════════════════════════════════════════
// 13. INITIALIZE ON PAGE LOAD
// ═══════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    // Start countdown timer if element exists
    const countdownElement = document.getElementById('countdown');
    if (countdownElement) {
        startCountdown(24);
    }

    console.log('🤖 AI Shop JavaScript loaded successfully!');
});


// ═══════════════════════════════════════════════════════════
// 14. SEARCH AUTOCOMPLETE (Amazon-style)
// ═══════════════════════════════════════════════════════════

const SearchAutocomplete = {
    timeout: null,

    init() {
        const input = document.getElementById('main-search-input');
        if (!input) return;

        input.addEventListener('input', (e) => {
            clearTimeout(this.timeout);
            const query = e.target.value.trim();

            if (query.length < 2) {
                this.hide();
                return;
            }

            this.timeout = setTimeout(() => this.search(query), 300);
        });

        // Hide on click outside
        document.addEventListener('click', (e) => {
            if (!input.contains(e.target)) {
                this.hide();
            }
        });
    },

    search(query) {
        trackSearchQuery(query);
        // Simulated search - in production, fetch from API
        fetch(`/api/search-suggestions/?q=${encodeURIComponent(query)}`)
            .then(r => r.json())
            .then(data => this.show(data.suggestions || []))
            .catch(() => this.hide());
    },

    show(suggestions) {
        this.hide();
        if (!suggestions.length) return;

        const dropdown = document.createElement('div');
        dropdown.id = 'search-dropdown';
        dropdown.style.cssText = `
            position: absolute;
            background: white;
            border: 1px solid #a6a6a6;
            border-top: none;
            width: 100%;
            z-index: 9999;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            border-radius: 0 0 4px 4px;
            max-height: 400px;
            overflow-y: auto;
        `;

        suggestions.forEach(s => {
            const item = document.createElement('div');
            item.style.cssText = 'padding: 8px 12px; cursor: pointer; font-size: 13px; display:flex; align-items:center; gap:10px;';
            item.innerHTML = `<i class="fas fa-search" style="color:#999;font-size:11px;"></i> ${s.title}`;

            item.addEventListener('mouseenter', () => item.style.background = '#f5f5f5');
            item.addEventListener('mouseleave', () => item.style.background = 'white');
            item.addEventListener('click', () => {
                if (s.id) {
                    window.location.href = `/product/${encodeURIComponent(s.id)}/`;
                    return;
                }
                window.location.href = `/products/?q=${encodeURIComponent(s.title)}`;
            });

            dropdown.appendChild(item);
        });

        const searchBar = document.querySelector('.navbar-search-bar');
        if (searchBar) {
            searchBar.style.position = 'relative';
            searchBar.appendChild(dropdown);
        }
    },

    hide() {
        const dropdown = document.getElementById('search-dropdown');
        if (dropdown) dropdown.remove();
    }
};

// Initialize search autocomplete
SearchAutocomplete.init();
// Quick view modal
function ensureQuickViewModal() {
    let modalEl = document.getElementById('quickViewModal');
    if (modalEl) return modalEl;

    const shell = document.createElement('div');
    shell.innerHTML = `
        <div class="modal fade" id="quickViewModal" tabindex="-1" aria-labelledby="quickViewModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title fw-bold" id="quickViewModalLabel">Quick View</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="text-center py-4">
                            <span class="spinner-border text-primary" aria-hidden="true"></span>
                            <p class="text-muted mt-2 mb-0">Loading product...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    modalEl = shell.firstElementChild;
    document.body.appendChild(modalEl);
    return modalEl;
}

function renderQuickViewContent(product, detailUrl) {
    const price = (typeof product.price === 'number' && product.price > 0) ? `Rs. ${product.price.toLocaleString()}` : 'Price unavailable';
    const rating = (typeof product.rating === 'number') ? product.rating.toFixed(1) : '0.0';
    const inStock = Number(product.stock || 0) > 0;

    return `
        <div class="row g-4 align-items-start">
            <div class="col-md-5">
                <img src="${product.image || ''}" alt="${product.title || 'Product image'}" class="img-fluid rounded border" style="width:100%;max-height:340px;object-fit:cover;">
            </div>
            <div class="col-md-7">
                <p class="text-muted mb-1">${product.category || 'Uncategorized'}</p>
                <h4 class="fw-bold mb-2">${product.title || 'Product'}</h4>
                <div class="d-flex align-items-center gap-3 mb-3">
                    <span class="badge ${inStock ? 'text-bg-success' : 'text-bg-danger'}">${inStock ? 'In stock' : 'Out of stock'}</span>
                    <span class="text-muted"><i class="fas fa-star text-warning me-1"></i>${rating}/5</span>
                </div>
                <h4 class="text-primary fw-bold mb-3">${price}</h4>
                <p class="text-muted">${product.description || 'No description available.'}</p>
                <div class="d-flex gap-2 mt-3">
                    ${inStock ? `<button type="button" class="btn btn-primary btn-add-cart" data-modal-add="${product.id}"><i class="fas fa-shopping-cart me-1"></i>Add to Cart</button>` : `<button type="button" class="btn btn-secondary" disabled><i class="fas fa-times-circle me-1"></i>Out of Stock</button>`}
                    <a href="${detailUrl}" class="btn btn-outline-primary">
                        <i class="fas fa-eye me-1"></i>View Details
                    </a>
                </div>
            </div>
        </div>
    `;
}

document.addEventListener('click', (event) => {
    const trigger = event.target.closest('.quick-view-trigger');
    if (!trigger) return;

    event.preventDefault();
    const quickViewUrl = trigger.dataset.quickViewUrl;
    const productUrl = trigger.dataset.productUrl;
    const productId = trigger.dataset.productId;
    if (!quickViewUrl) return;

    const modalEl = ensureQuickViewModal();
    const modalBody = modalEl.querySelector('.modal-body');
    modalBody.innerHTML = `
        <div class="text-center py-4">
            <span class="spinner-border text-primary" aria-hidden="true"></span>
            <p class="text-muted mt-2 mb-0">Loading product...</p>
        </div>
    `;
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();

    fetch(quickViewUrl)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            if (!data.success || !data.product) {
                throw new Error('Invalid quick view response');
            }
            modalBody.innerHTML = renderQuickViewContent(data.product, productUrl || `/product/${encodeURIComponent(data.product.id)}/`);
            if (productId) {
                trackInteraction(productId, 'click', { metadata: { source: 'quick_view' } });
            }
        })
        .catch((error) => {
            console.error('Quick view error:', error);
            modalBody.innerHTML = `
                <div class="alert alert-danger mb-0">
                    Could not load product preview. Please open the full product page.
                </div>
            `;
        });
});

document.addEventListener('click', (event) => {
    const addBtn = event.target.closest('[data-modal-add]');
    if (!addBtn) return;
    const productId = Number.parseInt(addBtn.dataset.modalAdd, 10);
    if (!Number.isFinite(productId)) return;
    addToCart(productId, 1, addBtn);
});

// ═══════════════════════════════════════════════════════════
// 15. PRODUCT IMAGE ZOOM (Amazon-style)
// ═══════════════════════════════════════════════════════════

function initImageZoom() {
    const img = document.getElementById('product-main-img');
    if (!img) return;

    const lens = document.createElement('div');
    lens.style.cssText = 'position:absolute;border:2px solid #FF9900;width:100px;height:100px;display:none;pointer-events:none;background:rgba(255,255,255,0.3);';

    img.parentElement.style.position = 'relative';
    img.parentElement.appendChild(lens);

    img.addEventListener('mousemove', (e) => {
        const rect = img.getBoundingClientRect();
        const x = e.clientX - rect.left - 50;
        const y = e.clientY - rect.top - 50;

        lens.style.left = Math.max(0, Math.min(x, img.width - 100)) + 'px';
        lens.style.top = Math.max(0, Math.min(y, img.height - 100)) + 'px';
        lens.style.display = 'block';
    });

    img.addEventListener('mouseleave', () => {
        lens.style.display = 'none';
    });
}

// Initialize image zoom on page load
initImageZoom();

// ═══════════════════════════════════════════════════════════
// 16. INTERACTION TRACKING (Background, Silent)
// ═══════════════════════════════════════════════════════════

function trackInteraction(productId, type, extra = {}) {
    const payload = {
        interaction_type: type
    };
    if (productId !== null && productId !== undefined) {
        payload.product_id = productId;
    }
    if (extra.query) {
        payload.query = extra.query;
    }
    if (extra.metadata) {
        payload.metadata = extra.metadata;
    }

    fetch('/track/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken() || getCookieCsrf()
        },
        body: JSON.stringify(payload),
        keepalive: type === 'click'
    }).catch(() => { });
}

function trackSearchQuery(query) {
    if (!query || query.length < 2) return;
    trackInteraction(null, 'search', {
        query: query,
        metadata: { source: 'autocomplete' }
    });
}
// Auto-track visible products using Intersection Observer
const productObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const productId = entry.target.dataset.productId;
            if (productId) {
                trackInteraction(productId, 'view');
                productObserver.unobserve(entry.target);
            }
        }
    });
}, { threshold: 0.5 });

// Observe all product cards
document.querySelectorAll('[data-product-id]').forEach(el => {
    productObserver.observe(el);
});

// ═══════════════════════════════════════════════════════════
// 17. LOADING SKELETON GENERATOR
// ═══════════════════════════════════════════════════════════

function showProductSkeletons(containerId, count = 4) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const skeletonHTML = `
        <div class="col-lg-3 col-md-4 col-6">
            <div class="product-card p-3">
                <div class="skeleton skeleton-img"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text short"></div>
                <div class="skeleton skeleton-price"></div>
            </div>
        </div>
    `;

    container.innerHTML = skeletonHTML.repeat(count);
}

// ═══════════════════════════════════════════════════════════
// 18. CART MANAGEMENT (LocalStorage + Session Sync)
// ═══════════════════════════════════════════════════════════

const Cart = {
    data: JSON.parse(localStorage.getItem('aiShopCart') || '{}'),

    add(productId, quantity = 1) {
        if (this.data[productId]) {
            this.data[productId].qty += quantity;
        } else {
            this.data[productId] = { qty: quantity };
        }

        this.save();
        this.updateBadge();

        // Sync with server
        fetch(`/cart/add/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken() || getCookieCsrf(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ quantity })
        })
            .then(r => r.json())
            .then(data => {
                this.showAddedAnimation(productId);
                showToast(`Added to Cart! (${this.count()} items)`, 'success');
            })
            .catch(() => showToast('Error adding to cart', 'error'));
    },

    remove(productId) {
        delete this.data[productId];
        this.save();
        this.updateBadge();
    },

    count() {
        return Object.values(this.data).reduce((sum, item) => sum + item.qty, 0);
    },

    save() {
        localStorage.setItem('aiShopCart', JSON.stringify(this.data));
    },

    updateBadge() {
        const badge = document.getElementById('cart-count-badge');
        if (badge) {
            badge.textContent = this.count();
            badge.style.display = this.count() > 0 ? 'flex' : 'none';
        }
    },

    showAddedAnimation(productId) {
        const btn = document.querySelector(`[data-product-id="${productId}"] .btn-add-cart`);
        if (btn) {
            const originalText = btn.textContent;
            btn.textContent = '✓ Added!';
            btn.style.background = '#007600';
            btn.style.color = 'white';

            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = '';
                btn.style.color = '';
            }, 1500);
        }
    }
};

// Initialize cart on page load
Cart.updateBadge();

// ═══════════════════════════════════════════════════════════
// 19. SMOOTH SCROLL TO TOP BUTTON
// ═══════════════════════════════════════════════════════════

const scrollToTopBtn = document.createElement('button');
scrollToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
scrollToTopBtn.style.cssText = `
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: var(--amazon-orange);
    color: white;
    border: none;
    cursor: pointer;
    display: none;
    z-index: 1000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
`;

scrollToTopBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

document.body.appendChild(scrollToTopBtn);

window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
        scrollToTopBtn.style.display = 'block';
    } else {
        scrollToTopBtn.style.display = 'none';
    }
});

// ═══════════════════════════════════════════════════════════
// 20. QUANTITY SELECTOR (Product Detail Page)
// ═══════════════════════════════════════════════════════════

function initQuantitySelector() {
    const minusBtn = document.getElementById('qty-minus');
    const plusBtn = document.getElementById('qty-plus');
    const qtyInput = document.getElementById('qty-input');

    if (!minusBtn || !plusBtn || !qtyInput) return;

    minusBtn.addEventListener('click', () => {
        const currentValue = parseInt(qtyInput.value) || 1;
        if (currentValue > 1) {
            qtyInput.value = currentValue - 1;
        }
    });

    plusBtn.addEventListener('click', () => {
        const currentValue = parseInt(qtyInput.value) || 1;
        const maxStock = parseInt(qtyInput.getAttribute('max')) || 999;
        if (currentValue < maxStock) {
            qtyInput.value = currentValue + 1;
        }
    });
}

// Initialize quantity selector
initQuantitySelector();

// ═══════════════════════════════════════════════════════════
// 21. LAZY LOADING IMAGES
// ═══════════════════════════════════════════════════════════

const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            const src = img.getAttribute('data-src');
            if (src) {
                img.src = src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        }
    });
});

// Observe all lazy images
document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
});

// ═══════════════════════════════════════════════════════════
// 22. FORM VALIDATION HELPERS
// ═══════════════════════════════════════════════════════════

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^(\+92|0)?[0-9]{10}$/;
    return re.test(phone.replace(/[\s-]/g, ''));
}

// Add real-time validation to forms
document.addEventListener('DOMContentLoaded', () => {
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function () {
            if (this.value && !validateEmail(this.value)) {
                this.classList.add('is-invalid');
                showToast('Please enter a valid email address', 'warning');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    });

    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('blur', function () {
            if (this.value && !validatePhone(this.value)) {
                this.classList.add('is-invalid');
                showToast('Please enter a valid phone number', 'warning');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    });
});

// ═══════════════════════════════════════════════════════════
// 23. FINAL INITIALIZATION
// ═══════════════════════════════════════════════════════════

console.log('🚀 AI Shop - Amazon-Style JavaScript Loaded Successfully!');
console.log('📦 Features: Cart, Search, Recommendations, Tracking, Animations');
console.log('🤖 ML-Powered Personalization Active');


