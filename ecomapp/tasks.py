# carts/tasks.py
from celery import shared_task
from .models import Cart

@shared_task
def merge_carts(anonymous_cart_id, user_cart_id):
    try:
        anonymous_cart = Cart.objects.get(id=anonymous_cart_id)
        user_cart = Cart.objects.get(id=user_cart_id)
        
        for item in anonymous_cart.items.all():
            existing_item = user_cart.items.filter(product=item.product).first()
            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                item.cart = user_cart
                item.save()
        
        anonymous_cart.delete()
        return True
    except Cart.DoesNotExist:
        return False