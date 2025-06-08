import redis
import redis
from django.conf import settings
from .models import Cart, CartItem
from django.db import transaction
import json


redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_CART_DB
)
class CartService:
    @staticmethod
    def _cache_cart(cart):
        cart_key = f"cart:{cart.id}"
        items = list(cart.items.values('product_id', 'quantity'))

        cart_data = {
            "id": cart.id,
            "user": cart.user.id if cart.user else None,
            "items": items,
            "total_items": cart.total_items(),
        }

        redis_client.set(cart_key, json.dumps(cart_data))
        redis_client.expire(cart_key, 3600)  # 1 hour
            
    @staticmethod
    def migrate_anonymous_cart(request, user):
        """
        Migrates anonymous cart to authenticated user's cart
        Handles both database and cache migration
        """
        if not request.session.session_key or not user.is_authenticated:
            return None
        
        # Get both carts
        anonymous_cart = Cart.objects.filter(
            session_key=request.session.session_key
        ).first()
        
        if not anonymous_cart:
            return None
            
        user_cart, created = Cart.objects.get_or_create(user=user)
        
        # Perform migration
        with transaction.atomic():
            for item in anonymous_cart.items.all():
                existing_item = user_cart.items.filter(
                    product=item.product
                ).first()
                
                if existing_item:
                    existing_item.quantity += item.quantity
                    existing_item.save()
                else:
                    item.cart = user_cart
                    item.save()
            
            # Clear old cart and session
            anonymous_cart.delete()
            if 'anonymous_cart_id' in request.session:
                del request.session['anonymous_cart_id']
            
            # Update both cache entries
            redis_client.delete(f"cart:{anonymous_cart.id}")
            CartService._cache_cart(user_cart)
        
        return user_cart

    @staticmethod
    def get_user_cart(request):
        """Unified cart getter that handles migration automatically"""
        if request.user.is_authenticated:
            # Check if we need to migrate
            if request.session.session_key and 'anonymous_cart_id' in request.session:
                cart = CartService.migrate_anonymous_cart(request, request.user)
                if cart:
                    return cart
            
            # Return normal user cart
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            cart, created = Cart.objects.get_or_create(
                session_key=request.session.session_key
            )
            if created:
                request.session['anonymous_cart_id'] = str(cart.id)
        
        # Ensure cache is populated
        cart_key = f"cart:{cart.id}"
        if created or not redis_client.exists(cart_key):
            CartService._cache_cart(cart)
        
        return cart

    