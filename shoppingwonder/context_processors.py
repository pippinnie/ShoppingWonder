from .models import Category, CartItem


def categories(request):
    categories = Category.objects.order_by("name").all()
    return {
        "categories": categories,
    }


def cart(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(shopper=request.user).order_by("product__title")
        cart_amount = 0
        for item in cart_items:
            cart_amount = cart_amount + item.get_amount()
        return {
            "cart_items": cart_items, "cart_count": cart_items.count(), "cart_amount": cart_amount,
        }
    return {
            "cart_items": [], "cart_count": 0, "cart_amount": 0.00,
        }
