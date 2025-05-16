// Main JavaScript for StyleShop E-commerce Website

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu functionality
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileMenuClose = document.querySelector('.mobile-menu-close');
    const mobileMenuBackdrop = document.querySelector('.mobile-menu-backdrop');
    const mobileDropdownToggles = document.querySelectorAll('.mobile-dropdown-toggle');
    
    if (mobileMenuToggle && mobileMenu && mobileMenuClose && mobileMenuBackdrop) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.add('active');
            mobileMenuBackdrop.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
        
        mobileMenuClose.addEventListener('click', function() {
            mobileMenu.classList.remove('active');
            mobileMenuBackdrop.classList.remove('active');
            document.body.style.overflow = '';
        });
        
        mobileMenuBackdrop.addEventListener('click', function() {
            mobileMenu.classList.remove('active');
            mobileMenuBackdrop.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    if (mobileDropdownToggles) {
        mobileDropdownToggles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                const dropdown = this.nextElementSibling;
                dropdown.classList.toggle('active');
                
                // Change icon
                if (dropdown.classList.contains('active')) {
                    this.innerHTML = '<i class="fas fa-minus"></i>';
                } else {
                    this.innerHTML = '<i class="fas fa-plus"></i>';
                }
            });
        });
    }
    
    // Quantity input functionality
    const decrementButtons = document.querySelectorAll('.decrement-qty');
    const incrementButtons = document.querySelectorAll('.increment-qty');
    const quantityInputs = document.querySelectorAll('.qty-input');
    
    decrementButtons.forEach((button, index) => {
        button.addEventListener('click', function() {
            let value = parseInt(quantityInputs[index].value);
            if (value > 1) {
                value--;
                quantityInputs[index].value = value;
            }
            
            // Trigger change event
            const event = new Event('change');
            quantityInputs[index].dispatchEvent(event);
        });
    });
    
    incrementButtons.forEach((button, index) => {
        button.addEventListener('click', function() {
            let value = parseInt(quantityInputs[index].value);
            value++;
            quantityInputs[index].value = value;
            
            // Trigger change event
            const event = new Event('change');
            quantityInputs[index].dispatchEvent(event);
        });
    });
    
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            let value = parseInt(this.value);
            if (isNaN(value) || value < 1) {
                this.value = 1;
            }
        });
    });
    
    // Product tabs functionality
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const target = this.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to current button and content
            this.classList.add('active');
            document.getElementById(target).classList.add('active');
        });
    });
    
    // Product gallery functionality
    const mainImage = document.querySelector('.product-main-image img');
    const thumbnails = document.querySelectorAll('.product-thumbnail img');
    
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            mainImage.src = this.src;
        });
    });
    
    // Accordion functionality for FAQ
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    
    accordionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const item = this.parentElement;
            
            // Toggle active class
            item.classList.toggle('active');
        });
    });
    
    // Rating selection in review form
    const ratingStars = document.querySelectorAll('.rating-star');
    const ratingInput = document.querySelector('input[name="rating"]');
    
    if (ratingStars.length && ratingInput) {
        ratingStars.forEach(star => {
            star.addEventListener('click', function() {
                const value = this.getAttribute('data-value');
                
                // Remove active class from all stars
                ratingStars.forEach(s => s.classList.remove('active'));
                
                // Add active class to selected star and all previous stars
                ratingStars.forEach(s => {
                    if (parseInt(s.getAttribute('data-value')) <= parseInt(value)) {
                        s.classList.add('active');
                    }
                });
                
                // Update hidden input
                ratingInput.value = value;
            });
        });
    }
    
    // Payment method selection in checkout
    const paymentMethods = document.querySelectorAll('.payment-method');
    const paymentInputs = document.querySelectorAll('.payment-method input[type="radio"]');
    
    paymentInputs.forEach(input => {
        input.addEventListener('change', function() {
            // Remove active class from all methods
            paymentMethods.forEach(method => method.classList.remove('active'));
            
            // Add active class to selected method
            this.closest('.payment-method').classList.add('active');
        });
    });
    
    // Shipping address toggle in checkout
    const shippingToggle = document.querySelector('#shipping-toggle');
    const shippingAddress = document.querySelector('.shipping-address');
    
    if (shippingToggle && shippingAddress) {
        shippingToggle.addEventListener('change', function() {
            if (this.checked) {
                shippingAddress.classList.add('active');
            } else {
                shippingAddress.classList.remove('active');
            }
        });
    }
    
    // Automatic dismissal of alert messages
    const alerts = document.querySelectorAll('.alert:not(.alert-important)');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
    
    // Handle AJAX forms for cart and wishlist
    const ajaxForms = document.querySelectorAll('.ajax-form');
    
    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Create FormData object
            const formData = new FormData(this);
            
            // Get the form action URL
            const url = this.getAttribute('action');
            
            // Get CSRF token
            const csrftoken = getCookie('csrftoken');
            
            // Send AJAX request
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    // Show success message
                    showMessage('success', data.message || 'Item added successfully!');
                    
                    // Update cart count if available
                    if (data.cart_total !== undefined) {
                        updateCartCount(data.cart_total);
                    }
                    
                    // If redirect URL is provided
                    if (data.redirect) {
                        setTimeout(() => {
                            window.location.href = data.redirect;
                        }, 1000);
                    }
                    
                    // If reload is needed
                    if (data.reload) {
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    }
                } else {
                    // Show error message
                    showMessage('danger', data.message || 'An error occurred. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('danger', 'An error occurred. Please try again.');
            });
        });
    });
    
    // Function to show message
    function showMessage(type, text) {
        const messagesContainer = document.querySelector('.messages-container .container');
        if (messagesContainer) {
            const message = document.createElement('div');
            message.className = `alert alert-${type}`;
            message.textContent = text;
            
            messagesContainer.appendChild(message);
            
            // Remove message after 5 seconds
            setTimeout(() => {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.remove();
                }, 500);
            }, 5000);
        }
    }
    
    // Function to update cart count
    function updateCartCount(count) {
        const cartCount = document.querySelector('.cart-count');
        if (cartCount) {
            cartCount.textContent = count;
            
            // Animation effect
            cartCount.classList.add('update');
            setTimeout(() => {
                cartCount.classList.remove('update');
            }, 500);
        }
    }
    
    // Function to get cookie by name (for CSRF token)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Price range filter in shop sidebar
    const priceSlider = document.querySelector('.price-slider');
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    
    if (priceSlider && minPriceInput && maxPriceInput) {
        // Initialize values
        let minPrice = 0;
        let maxPrice = 1000;
        
        // Get URL parameters if available
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('min_price')) {
            minPrice = parseInt(urlParams.get('min_price'));
            minPriceInput.value = minPrice;
        }
        if (urlParams.has('max_price')) {
            maxPrice = parseInt(urlParams.get('max_price'));
            maxPriceInput.value = maxPrice;
        }
        
        // Update inputs when slider changes
        // Note: This is a placeholder for a slider library like noUiSlider
        // In a real implementation, you would initialize the slider library here
    }
    
    // Filter checkboxes in shop sidebar
    const filterCheckboxes = document.querySelectorAll('.filter-checkboxes input[type="checkbox"]');
    
    if (filterCheckboxes.length) {
        // Set initial state from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        
        if (urlParams.has('on_sale') && urlParams.get('on_sale') === 'true') {
            document.getElementById('filter-sale').checked = true;
        }
        
        if (urlParams.has('is_new') && urlParams.get('is_new') === 'true') {
            document.getElementById('filter-new').checked = true;
        }
        
        if (urlParams.has('is_featured') && urlParams.get('is_featured') === 'true') {
            document.getElementById('filter-featured').checked = true;
        }
    }
    
    // Shop filter toggle for mobile
    const filterToggleBtn = document.querySelector('.filter-toggle-btn');
    const shopSidebar = document.querySelector('.shop-sidebar');
    
    if (filterToggleBtn && shopSidebar) {
        filterToggleBtn.addEventListener('click', function() {
            shopSidebar.classList.toggle('active');
            
            // Add backdrop when sidebar is active
            if (shopSidebar.classList.contains('active')) {
                const backdrop = document.createElement('div');
                backdrop.className = 'sidebar-backdrop';
                backdrop.style.position = 'fixed';
                backdrop.style.top = '0';
                backdrop.style.left = '0';
                backdrop.style.width = '100%';
                backdrop.style.height = '100%';
                backdrop.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
                backdrop.style.zIndex = '998';
                document.body.appendChild(backdrop);
                
                // Close sidebar when backdrop is clicked
                backdrop.addEventListener('click', function() {
                    shopSidebar.classList.remove('active');
                    this.remove();
                });
            } else {
                const backdrop = document.querySelector('.sidebar-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
            }
        });
    }
    
    // Newsletter form submission
    const newsletterForm = document.querySelector('.newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Create FormData object
            const formData = new FormData(this);
            
            // Get the form action URL
            const url = this.getAttribute('action');
            
            // Get CSRF token
            const csrftoken = getCookie('csrftoken');
            
            // Send AJAX request
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    // Show success message
                    showMessage('success', data.message || 'Thank you for subscribing to our newsletter!');
                    
                    // Clear form
                    this.reset();
                } else {
                    // Show error message
                    showMessage('danger', data.message || 'An error occurred. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('danger', 'An error occurred. Please try again.');
            });
        });
    }
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Back to top button
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
    
    // Initialize AOS (Animate on Scroll) if available
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true
        });
    }
});