# carts/middleware.py
from django.utils.deprecation import MiddlewareMixin
from .services import CartService

class CartMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not hasattr(request, 'session'):
            return
        
        # Ensure session exists
        if not request.session.session_key:
            request.session.create()
        
        # Attach cart to request object
        request.cart = CartService.get_user_cart(request)