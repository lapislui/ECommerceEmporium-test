from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import (
    Category, Product, Order, OrderItem, 
    UserProfile, Review, Wishlist, Newsletter, ContactMessage
)
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm, 
    ProductForm, CategoryForm, ReviewForm, ContactForm, 
    NewsletterForm, CheckoutForm, PasswordChangeForm
)
from .cart import Cart


def home(request):
    featured_products = Product.objects.filter(is_featured=True, is_available=True)[:8]
    bestsellers = Product.objects.filter(is_bestseller=True, is_available=True)[:8]
    new_arrivals = Product.objects.filter(is_new=True, is_available=True)[:8]
    on_sale = Product.objects.filter(is_on_sale=True, is_available=True)[:8]
    
    context = {
        'featured_products': featured_products,
        'bestsellers': bestsellers,
        'new_arrivals': new_arrivals,
        'on_sale': on_sale,
    }
    return render(request, 'home_new.html', context)


def product_list(request):
    products = Product.objects.filter(is_available=True)
    
    # Filtering
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', '')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'products': page_obj,
        'search_query': search_query,
        'category_slug': category_slug,
        'sort_by': sort_by,
    }
    return render(request, 'product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    reviews = product.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]
    
    # Add to cart form
    if request.method == 'POST':
        cart = Cart(request)
        cart.add(product=product, quantity=int(request.POST.get('quantity', 1)))
        messages.success(request, f"Added {product.name} to your cart.")
        return redirect('product_detail', slug=slug)
    
    # Review form
    review_form = None
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(product=product, user=request.user)
        except Review.DoesNotExist:
            review_form = ReviewForm()
    
    # Check if in wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    
    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
        'user_review': user_review,
        'related_products': related_products,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'product_detail.html', context)


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user already reviewed this product
    try:
        review = Review.objects.get(product=product, user=request.user)
        messages.error(request, "You have already reviewed this product.")
        return redirect('product_detail', slug=product.slug)
    except Review.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Your review has been added.")
            return redirect('product_detail', slug=product.slug)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'product_reviews.html', context)


def cart_detail(request):
    cart = Cart(request)
    
    context = {
        'cart': cart,
    }
    return render(request, 'cart.html', context)


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    return JsonResponse({'status': 'ok', 'cart_total': len(cart)})


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.update(product=product, quantity=quantity)
    return JsonResponse({'status': 'ok'})


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return JsonResponse({'status': 'ok'})


@login_required
def checkout(request):
    cart = Cart(request)
    
    # Check if cart is empty
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('cart_detail')
    
    # Get user profile data if exists
    initial_data = {}
    try:
        profile = request.user.profile
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': profile.phone,
            'address': profile.address,
            'city': profile.city,
            'state': profile.state,
            'postal_code': profile.postal_code,
            'country': profile.country,
        }
    except UserProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, initial=initial_data)
        if form.is_valid():
            # Create order
            order = Order.objects.create(
                user=request.user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                postal_code=form.cleaned_data['postal_code'],
                country=form.cleaned_data['country'],
                order_notes=form.cleaned_data['order_notes'],
                shipping_cost=form.cleaned_data['shipping_method'],
                total_paid=cart.get_total_price() + form.cleaned_data['shipping_method'],
            )
            
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
            
            # Clear cart
            cart.clear()
            
            # Store order ID in session for order success page
            request.session['last_order_id'] = order.id
            
            messages.success(request, "Your order has been placed successfully.")
            return redirect('order_success')
    else:
        form = CheckoutForm(initial=initial_data)
    
    context = {
        'cart': cart,
        'form': form,
    }
    return render(request, 'checkout.html', context)


@login_required
def order_success(request):
    order_id = request.session.get('last_order_id')
    if not order_id:
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'order_success.html', context)


@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders.html', context)


@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'track_order.html', context)


def categories(request):
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'categories': categories,
    }
    return render(request, 'categories.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_available=True)
    
    # Sorting
    sort_by = request.GET.get('sort', '')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'products': page_obj,
        'sort_by': sort_by,
    }
    return render(request, 'category_detail.html', context)


def search_results(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query) |
        Q(category__name__icontains=query),
        is_available=True
    ).distinct()
    
    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'search_results.html', context)


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'wishlist.html', context)


@login_required
@require_POST
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if already in wishlist
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f"{product.name} has been added to your wishlist.")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")
    
    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'created': created})
    
    # Otherwise redirect back to product page
    return redirect('product_detail', slug=product.slug)


@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    product_name = wishlist_item.product.name
    wishlist_item.delete()
    
    messages.success(request, f"{product_name} has been removed from your wishlist.")
    
    # If AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    
    # Otherwise redirect back to wishlist
    return redirect('wishlist')


def featured_products(request):
    products = Product.objects.filter(is_featured=True, is_available=True)
    
    context = {
        'products': products,
        'title': 'Featured Products',
    }
    return render(request, 'featured_products.html', context)


def best_sellers(request):
    products = Product.objects.filter(is_bestseller=True, is_available=True)
    
    context = {
        'products': products,
        'title': 'Best Sellers',
    }
    return render(request, 'best_sellers.html', context)


def new_arrivals(request):
    products = Product.objects.filter(is_new=True, is_available=True)
    
    context = {
        'products': products,
        'title': 'New Arrivals',
    }
    return render(request, 'new_arrivals.html', context)


def on_sale_products(request):
    products = Product.objects.filter(is_on_sale=True, is_available=True)
    
    context = {
        'products': products,
        'title': 'On Sale Products',
    }
    return render(request, 'on_sale_products.html', context)


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent. We'll get back to you soon!")
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
    }
    return render(request, 'contact.html', context)


def faq(request):
    return render(request, 'faq.html')


def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')


def privacy_policy(request):
    return render(request, 'privacy_policy.html')


def newsletter_signup(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "You have been subscribed to our newsletter!")
            return redirect('home')
    else:
        form = NewsletterForm()
    
    context = {
        'form': form,
    }
    return render(request, 'newsletter_signup.html', context)


def returns(request):
    return render(request, 'returns.html')


def support(request):
    return render(request, 'support.html')


def user_signup(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            # Login the user
            login(request, user)
            messages.success(request, "Account created successfully. Welcome to our store!")
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'signup.html', context)


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'home')
                messages.success(request, "You have been logged in successfully.")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
    }
    return render(request, 'login.html', context)


@login_required
def profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'profile': profile,
        'orders': orders,
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            # Update User model fields
            user = request.user
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.save()
            
            # Update profile
            form.save()
            
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        })
    
    context = {
        'form': form,
    }
    return render(request, 'edit_profile.html', context)


@login_required
def change_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Verify password
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            user.email = email
            user.save()
            messages.success(request, "Your email has been updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Invalid password.")
    
    return render(request, 'change_email.html')


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            user = request.user
            if user.check_password(form.cleaned_data['old_password']):
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                # Re-authenticate user
                login(request, authenticate(
                    username=user.username,
                    password=form.cleaned_data['new_password']
                ))
                messages.success(request, "Your password has been changed successfully.")
                return redirect('profile')
            else:
                messages.error(request, "Your old password was entered incorrectly.")
    else:
        form = PasswordChangeForm()
    
    context = {
        'form': form,
    }
    return render(request, 'password_change.html', context)


@staff_member_required
def dashboard(request):
    # Count total products, categories, orders
    product_count = Product.objects.count()
    category_count = Category.objects.count()
    order_count = Order.objects.count()
    user_count = User.objects.count()
    
    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:10]
    
    # Order status counts
    order_status_counts = Order.objects.values('status').annotate(count=Count('status'))
    
    # Popular products (most ordered)
    popular_products = Product.objects.annotate(
        times_ordered=Count('order_items')
    ).order_by('-times_ordered')[:5]
    
    context = {
        'product_count': product_count,
        'category_count': category_count,
        'order_count': order_count,
        'user_count': user_count,
        'recent_orders': recent_orders,
        'order_status_counts': order_status_counts,
        'popular_products': popular_products,
    }
    return render(request, 'dashboard.html', context)


@staff_member_required
def report_page(request):
    # Orders by status
    orders_by_status = Order.objects.values('status').annotate(count=Count('status'))
    
    # Orders by date (last 30 days)
    from datetime import datetime, timedelta
    start_date = datetime.now() - timedelta(days=30)
    orders_by_date = Order.objects.filter(
        created_at__gte=start_date
    ).values('created_at__date').annotate(
        count=Count('id'),
        total=Sum('total_paid')
    ).order_by('created_at__date')
    
    # Top selling products
    top_products = Product.objects.annotate(
        total_sold=Sum('order_items__quantity')
    ).order_by('-total_sold')[:10]
    
    context = {
        'orders_by_status': orders_by_status,
        'orders_by_date': orders_by_date,
        'top_products': top_products,
    }
    return render(request, 'report_page.html', context)


@staff_member_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' has been added successfully.")
            return redirect('product_detail', slug=product.slug)
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Add Product',
    }
    return render(request, 'add_product.html', context)


@staff_member_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product '{product.name}' has been updated successfully.")
            return redirect('product_detail', slug=product.slug)
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': 'Edit Product',
    }
    return render(request, 'edit_product.html', context)


@staff_member_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' has been added successfully.")
            return redirect('category_detail', slug=category.slug)
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Add Category',
    }
    return render(request, 'add_category.html', context)


@staff_member_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' has been updated successfully.")
            return redirect('category_detail', slug=category.slug)
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': 'Edit Category',
    }
    return render(request, 'edit_category.html', context)
