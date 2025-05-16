from .cart import Cart
from .models import Category

def cart_processor(request):
    """
    Context processor to make cart available to all templates.
    """
    return {'cart': Cart(request)}

def categories_processor(request):
    """
    Context processor to make categories available to all templates.
    """
    categories = Category.objects.filter(is_active=True)
    return {'categories_list': categories}
