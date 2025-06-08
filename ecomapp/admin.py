from django.contrib import admin
from .models import CustomUser
from .models import Category, SubCategory, Brand, Product
from django.utils import timezone
from django.contrib import admin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "is_active", "is_staff")
    list_filter = ("is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name","username", "last_name")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "is_active")}),
        
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2"),
        }),
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug')
    list_filter = ('category',)
    search_fields = ('name', 'slug')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'subcategory', 'brand',
        'price', 'discounted_price', 'quantity',
        'stock_status', 'is_available', 'created_at'
    )
    list_filter = (
        'category', 'subcategory', 'brand', 'gender'
    )
    search_fields = ('name', 'sku', 'category__name', 'subcategory__name', 'brand__name')
    autocomplete_fields = ['category', 'subcategory', 'brand']
    readonly_fields = ('stock_status', 'is_available', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

