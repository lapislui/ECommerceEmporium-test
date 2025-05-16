from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home, product and category pages
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('categories/', views.categories, name='categories'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # Cart and checkout
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),
    path('orders/', views.orders, name='orders'),
    path('track-order/<int:order_id>/', views.track_order, name='track_order'),
    
    # User authentication
    path('signup/', views.user_signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/email/change/', views.change_email, name='change_email'),
    path('profile/password/change/', views.password_change, name='password_change'),
    
    # Password reset
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html',
            email_template_name='password_reset_email.html',
            success_url='/password-reset/done/'
        ), 
        name='password_reset'),
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
        ), 
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html',
            success_url='/password-reset-complete/'
        ), 
        name='password_reset_confirm'),
    path('password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset_complete.html'
        ), 
        name='password_reset_complete'),
    
    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Reviews
    path('product-review/<int:product_id>/', views.add_review, name='add_review'),
    
    # Search
    path('search/', views.search_results, name='search_results'),
    
    # Featured collections
    path('featured-products/', views.featured_products, name='featured_products'),
    path('best-sellers/', views.best_sellers, name='best_sellers'),
    path('new-arrivals/', views.new_arrivals, name='new_arrivals'),
    path('on-sale/', views.on_sale_products, name='on_sale_products'),
    
    # Info pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),
    path('returns/', views.returns, name='returns'),
    path('support/', views.support, name='support'),
    
    # Admin
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reports/', views.report_page, name='report_page'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('add-category/', views.add_category, name='add_category'),
    path('edit-category/<int:category_id>/', views.edit_category, name='edit_category'),
]
