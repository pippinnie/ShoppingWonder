from .models import Category, CartItem, Product


def categories(request):
    categories = Category.objects.order_by("name").all()
    return {
        "categories": categories,
    }


def cart(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(shopper=request.user).order_by("product__title")
        cart_amount = 0
        for cart_item in cart_items:
            # If remaining stock is less than cart qty, update cart item to be equal to the remaining qty
            if cart_item.product.remaining_qty < cart_item.quantity:
                if cart_item.product.remaining_qty == 0:
                    cart_item.delete()
                    continue

                cart_item.quantity = cart_item.product.remaining_qty
                cart_item.save()

            # Accumulate item subtotal (qty * price)
            cart_amount = cart_amount + cart_item.get_amount()

        return {
            "cart_items": cart_items, "cart_count": cart_items.count(), "cart_amount": cart_amount,
        }

    return {
            "cart_items": [], "cart_count": 0, "cart_amount": 0.00,
        }
