from .serializers import CustomUserSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count, Min, Max
from django.core.paginator import Paginator
from .models import Product, Category, SubCategory, Brand
from taggit.models import Tag
from .services import CartService

def shared_context(request):
    return {
        'site_name': 'Buyzaar',
        'categories': Category.objects.all(),
        'products': Product.objects.filter(quantity__gt=0),
        'subcategory': SubCategory.objects.all(),
    }
    
def cart_context(request):
    cart = CartService.get_user_cart(request)
    return {
        'cart_total_items': cart.total_items() if cart else 0
    }
