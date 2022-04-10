from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Stock


@receiver(post_save, sender=Stock)
def update_product_from_stock(sender, **kwargs):
    if kwargs["created"]:
        # Get stock quantity newly created
        stock = kwargs["instance"]
        qty = stock.quantity
        stock.product.adjust_qty(qty)