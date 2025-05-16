from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    UserProfile, Product, Category, Review, 
    ContactMessage, Newsletter, Order
)


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("New passwords don't match.")
        
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'state', 'postal_code', 'country']
        exclude = ['user']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'description', 'price', 'image_url',
            'is_available', 'is_featured', 'is_bestseller', 'is_new',
            'is_on_sale', 'discount_price', 'stock'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        is_on_sale = cleaned_data.get('is_on_sale')
        discount_price = cleaned_data.get('discount_price')
        price = cleaned_data.get('price')
        
        if is_on_sale and not discount_price:
            raise forms.ValidationError("Discount price is required for products on sale.")
        
        if discount_price and discount_price >= price:
            raise forms.ValidationError("Discount price must be less than the regular price.")
        
        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image_url', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['email']


class CheckoutForm(forms.Form):
    SHIPPING_CHOICES = [
        (5.99, 'Standard Shipping - $5.99'),
        (12.99, 'Express Shipping - $12.99'),
    ]
    
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    address = forms.CharField(max_length=250)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)
    country = forms.CharField(max_length=100)
    shipping_method = forms.DecimalField(
        widget=forms.RadioSelect(choices=SHIPPING_CHOICES)
    )
    order_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
