# carts/api.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.cache import cache
from .models import Cart, CartItem, Product
from .serializers import CartSerializer, CartItemSerializer
from .services import CartService
from django.db import transaction

class CartViewSet(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    
    def get_queryset(self):
        return Cart.objects.none()  # We override all methods
    
    def retrieve(self, request, *args, **kwargs):
        cart = CartService.get_or_create_cart(request)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    # @action(detail=False, methods=['post'])
    # def add_item(self, request):
    #     cart = CartService.get_or_create_cart(request)
    #     serializer = CartItemSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
        
    #     try:
    #         product = Product.objects.get(id=serializer.validated_data['product_id'], is_active=True)
    #     except Product.DoesNotExist:
    #         return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
    #     # Check inventory
    #     if product.quantity < serializer.validated_data['quantity']:
    #         return Response({"error": "Insufficient inventory"}, status=status.HTTP_400_BAD_REQUEST)
        
    #     # Atomic transaction
    #     with transaction.atomic():
    #         cart_item, created = CartItem.objects.get_or_create(
    #             cart=cart,
    #             product=product,
    #             defaults={
    #                 'quantity': serializer.validated_data['quantity'],
    #                 'price': product.price
    #             }
    #         )
            
    #         if not created:
    #             cart_item.quantity += serializer.validated_data['quantity']
    #             cart_item.save()
            
    #         # Update Redis cache
    #         CartService._cache_cart(cart)
        
    #     return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def merge_carts(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)
            
        if 'anonymous_cart_id' not in request.session:
            return Response({"message": "No cart to merge"}, status=200)
            
        result = CartService.migrate_cart(
            request.session['anonymous_cart_id'],
            request.user.id
        )
        
        if result:
            del request.session['anonymous_cart_id']
            return Response({"message": "Cart merged successfully"})
        
        return Response({"error": "Merge failed"}, status=400)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = CartService.get_or_create_cart(request)
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            with transaction.atomic():
                # Lock the product row
                product = Product.objects.select_for_update().get(id=product_id)

                if product.quantity < quantity:
                    return Response(
                        {"error": f"Only {product.quantity} left in stock"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={
                        'quantity': quantity,
                        'price': product.price
                    }
                )
                
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()

                # Reduce product stock
                product.quantity -= quantity
                product.save()

                # Update cache if applicable
                CartService._cache_cart(cart)

        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)