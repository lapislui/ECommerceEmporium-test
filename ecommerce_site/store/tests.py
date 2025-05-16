from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Product, Order, OrderItem, UserProfile, Review, Wishlist, Newsletter, ContactMessage
from decimal import Decimal


class CategoryModelTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            description='Test Description',
            image_url='https://example.com/image.jpg'
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')
        self.assertTrue(self.category.is_active)


class ProductModelTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            description='Test Description',
            price=Decimal('99.99'),
            image_url='https://example.com/image.jpg',
            stock=10
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.slug, 'test-product')
        self.assertEqual(self.product.price, Decimal('99.99'))
        self.assertTrue(self.product.is_available)
        self.assertEqual(self.product.stock, 10)

    def test_get_discount_percentage(self):
        # No discount
        self.assertEqual(self.product.get_discount_percentage(), 0)
        
        # With discount
        self.product.is_on_sale = True
        self.product.discount_price = Decimal('79.99')
        self.product.save()
        self.assertEqual(self.product.get_discount_percentage(), 20)


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            description='Test Description',
            price=Decimal('99.99'),
            image_url='https://example.com/image.jpg',
            stock=10
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_product_detail_view(self):
        response = self.client.get(reverse('product_detail', args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product_detail.html')
        self.assertEqual(response.context['product'], self.product)

    def test_category_detail_view(self):
        response = self.client.get(reverse('category_detail', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'category_detail.html')
        self.assertEqual(response.context['category'], self.category)

    def test_login_required_views(self):
        # Views that require login should redirect to login page
        wishlist_url = reverse('wishlist')
        profile_url = reverse('profile')
        checkout_url = reverse('checkout')
        
        response = self.client.get(wishlist_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next={wishlist_url}')
        
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next={profile_url}')
        
        response = self.client.get(checkout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next={checkout_url}')

    def test_authenticated_views(self):
        # Login the user
        self.client.login(username='testuser', password='testpassword')
        
        # Test profile view
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        
        # Test wishlist view
        response = self.client.get(reverse('wishlist'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wishlist.html')


class CartTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            description='Test Description',
            price=Decimal('99.99'),
            image_url='https://example.com/image.jpg',
            stock=10
        )

    def test_add_to_cart(self):
        # Add product to cart
        response = self.client.post(
            reverse('cart_add', args=[self.product.id]),
            {'quantity': 2},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        
        # Check cart page
        response = self.client.get(reverse('cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart.html')


class OrderTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            description='Test Description',
            price=Decimal('99.99'),
            image_url='https://example.com/image.jpg',
            stock=10
        )
        
        # Create an order
        self.order = Order.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='1234567890',
            address='123 Test Street',
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='Test Country',
            shipping_cost=Decimal('5.99'),
            total_paid=Decimal('105.98'),
        )
        
        # Create order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=Decimal('99.99'),
            quantity=1
        )

    def test_order_creation(self):
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.status, 'pending')
        self.assertEqual(self.order.total_paid, Decimal('105.98'))
        
        # Test get_total_cost method
        self.assertEqual(self.order.get_total_cost(), Decimal('105.98'))
        
        # Test order item
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.price, Decimal('99.99'))
        self.assertEqual(self.order_item.quantity, 1)
        self.assertEqual(self.order_item.get_cost(), Decimal('99.99'))


class NewsletterTestCase(TestCase):
    def test_newsletter_signup(self):
        response = self.client.post(
            reverse('newsletter_signup'),
            {'email': 'test@example.com'}
        )
        self.assertEqual(response.status_code, 302)  # Redirects after submission
        
        # Check if newsletter subscription was created
        self.assertTrue(Newsletter.objects.filter(email='test@example.com').exists())


class ContactMessageTestCase(TestCase):
    def test_contact_form(self):
        response = self.client.post(
            reverse('contact'),
            {
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': 'Test Subject',
                'message': 'Test Message'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirects after submission
        
        # Check if contact message was created
        self.assertTrue(ContactMessage.objects.filter(email='test@example.com').exists())
