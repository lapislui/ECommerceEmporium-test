// Main eCommerce JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu functionality
    initMobileMenu();
    
    // Back to top button functionality 
    initBackToTop();
    
    // Product quantity buttons
    initQuantityButtons();
    
    // Product image gallery
    initImageGallery();
    
    // Initialize tooltips and other UI elements
    initUI();
});

// Mobile Menu Functions
function initMobileMenu() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileMenuClose = document.querySelector('.mobile-menu-close');
    const mobileMenuBackdrop = document.querySelector('.mobile-menu-backdrop');
    const mobileDropdownToggles = document.querySelectorAll('.mobile-dropdown-toggle');
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.add('active');
            mobileMenuBackdrop.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }
    
    if (mobileMenuClose) {
        mobileMenuClose.addEventListener('click', closeMobileMenu);
    }
    
    if (mobileMenuBackdrop) {
        mobileMenuBackdrop.addEventListener('click', closeMobileMenu);
    }
    
    // Mobile submenu toggles
    if (mobileDropdownToggles.length > 0) {
        mobileDropdownToggles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                const parent = this.parentElement;
                const submenu = parent.querySelector('.mobile-submenu');
                if (submenu) {
                    if (submenu.style.display === 'block') {
                        submenu.style.display = 'none';
                        this.innerHTML = '<i class="fas fa-plus"></i>';
                    } else {
                        submenu.style.display = 'block';
                        this.innerHTML = '<i class="fas fa-minus"></i>';
                    }
                }
            });
        });
    }
    
    function closeMobileMenu() {
        mobileMenu.classList.remove('active');
        mobileMenuBackdrop.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Back to top button
function initBackToTop() {
    const backToTopBtn = document.querySelector('.back-to-top');
    
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.classList.add('active');
            } else {
                backToTopBtn.classList.remove('active');
            }
        });
        
        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

// Product quantity buttons
function initQuantityButtons() {
    const minusBtns = document.querySelectorAll('.quantity-minus');
    const plusBtns = document.querySelectorAll('.quantity-plus');
    
    if (minusBtns.length > 0) {
        minusBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const input = this.parentElement.querySelector('input');
                const value = parseInt(input.value);
                if (value > 1) {
                    input.value = value - 1;
                    // Trigger change event
                    const event = new Event('change');
                    input.dispatchEvent(event);
                }
            });
        });
    }
    
    if (plusBtns.length > 0) {
        plusBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const input = this.parentElement.querySelector('input');
                const value = parseInt(input.value);
                const max = parseInt(input.getAttribute('max') || 999);
                if (value < max) {
                    input.value = value + 1;
                    // Trigger change event
                    const event = new Event('change');
                    input.dispatchEvent(event);
                }
            });
        });
    }
}

// Product image gallery
function initImageGallery() {
    const mainImage = document.querySelector('.product-main-image img');
    const thumbnails = document.querySelectorAll('.product-thumbnail');
    
    if (mainImage && thumbnails.length > 0) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function() {
                const imgSrc = this.getAttribute('data-img');
                mainImage.src = imgSrc;
                
                // Update active class
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }
}

// Initialize UI elements
function initUI() {
    // Add to cart notification
    const addToCartBtns = document.querySelectorAll('.add-to-cart');
    
    if (addToCartBtns.length > 0) {
        addToCartBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                if (!btn.classList.contains('disabled')) {
                    showNotification('Product added to cart', 'success');
                }
            });
        });
    }
    
    // Add to wishlist functionality
    const wishlistBtns = document.querySelectorAll('.add-to-wishlist');
    
    if (wishlistBtns.length > 0) {
        wishlistBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                if (btn.classList.contains('in-wishlist')) {
                    btn.classList.remove('in-wishlist');
                    showNotification('Product removed from wishlist', 'info');
                } else {
                    btn.classList.add('in-wishlist');
                    showNotification('Product added to wishlist', 'success');
                }
            });
        });
    }
    
    // Product quick view
    const quickViewBtns = document.querySelectorAll('.quick-view');
    const quickViewModal = document.querySelector('.quick-view-modal');
    const quickViewClose = document.querySelector('.quick-view-close');
    
    if (quickViewBtns.length > 0 && quickViewModal) {
        quickViewBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                quickViewModal.classList.add('active');
                document.body.style.overflow = 'hidden';
                
                // Here you would load product data via AJAX
                // For demo purposes, we'll just show the modal
            });
        });
        
        if (quickViewClose) {
            quickViewClose.addEventListener('click', function() {
                quickViewModal.classList.remove('active');
                document.body.style.overflow = '';
            });
        }
    }
}

// Helper function to show notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Add active class after a small delay to trigger animation
    setTimeout(() => {
        notification.classList.add('active');
    }, 10);
    
    // Add close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', function() {
        removeNotification(notification);
    });
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        removeNotification(notification);
    }, 3000);
    
    function removeNotification(notif) {
        notif.classList.remove('active');
        setTimeout(() => {
            document.body.removeChild(notif);
        }, 300);
    }
}

// Add CSS for notifications
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    transform: translateX(120%);
    transition: transform 0.3s ease;
}

.notification.active {
    transform: translateX(0);
}

.notification-content {
    background-color: #fff;
    color: #333;
    padding: 15px 20px;
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-width: 250px;
}

.notification-success .notification-content {
    border-left: 4px solid #28a745;
}

.notification-error .notification-content {
    border-left: 4px solid #dc3545;
}

.notification-info .notification-content {
    border-left: 4px solid #17a2b8;
}

.notification-warning .notification-content {
    border-left: 4px solid #ffc107;
}

.notification-close {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    margin-left: 10px;
    color: #777;
}
`;
document.head.appendChild(notificationStyles);

// Add Click events for mobile submenu toggles
document.addEventListener('click', function(e) {
    const mobileMenuItems = document.querySelectorAll('.mobile-menu-items > li > a');
    
    mobileMenuItems.forEach(item => {
        if (e.target === item && item.nextElementSibling && item.nextElementSibling.classList.contains('mobile-submenu')) {
            e.preventDefault();
            const submenu = item.nextElementSibling;
            if (submenu.style.display === 'block') {
                submenu.style.display = 'none';
            } else {
                submenu.style.display = 'block';
            }
        }
    });
});