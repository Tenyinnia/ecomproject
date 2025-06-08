# serializers.py
from rest_framework import serializers
from taggit.serializers import (TagListSerializerField, TaggitSerializer)
from .models import Product, CustomUser, Cart, CartItem

class ProductSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()  # This enables sending/receiving tags as a list

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'description', 'price', 'discounted_price',
            'quantity', 'sku', 'image', 'is_available', 'tags', 'created_at'
        ]


class CustomUserSerializer(serializers.ModelSerializer):
    password1= serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 'phone_number',
            'password1', 'password2'
        ]

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password1')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source='product'
    )
    price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price']
        read_only_fields = ['id', 'price']
        extra_kwargs = {
            'quantity': {'min_value': 1}
        }

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity', 1)

        if product and product.quantity < quantity:
            raise serializers.ValidationError(
                f"Only {product.quantity} items available in stock"
            )
        return data

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'updated_at', 'items', 'total', 'item_count']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total(self, obj):
        return sum(item.price * item.quantity for item in obj.items.all())

    def get_item_count(self, obj):
        return obj.items.count()

class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, data):
        product = data['product_id']
        if product.quantity < data['quantity']:
            raise serializers.ValidationError(
                f"Only {product.quantity} items available in stock"
            )
        if  not product.quantity > 0:
            raise serializers.ValidationError("Product out of stock")
        return data
