from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django import forms
from django.contrib.auth.models import User
#Create your models here.
from django.contrib.auth import get_user_model
from django.conf import settings
import secrets
from django_countries.fields import CountryField
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractUser, AbstractBaseUser
import os
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import random
import string
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from taggit.managers import TaggableManager
from smart_selects.db_fields import ChainedForeignKey

class CustomUserManager(BaseUserManager):
    """Manager for CustomUser with different roles."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Creates a user with a generated temporary password if none is provided."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)

        # Generate a random temporary password
        temp_password = password or self.generate_random_password()

        user = self.model(email=email, **extra_fields)
        user.set_password(temp_password)
        user.first_login = True  # Enforce password change on first login
        user.save(using=self._db)

        # Send the temporary password via email
        self.send_temporary_password(email, temp_password)

        return user

    def create_staff(self, email, first_name, last_name):
        """Creates a Staff user with permissions to manage tutors."""
        return self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not extra_fields.get('phone_number'):
            raise ValueError('Superusers must have a phone number.')

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
    
    def send_temporary_password(self, email, password):
        subject = "Your Temporary Account Password"
        message = f"Hello,\n\nYour temporary password is: {password}\nPlease change it after logging in."
        send_mail(subject, message, "smartlearnk12@gmail.com", [email])

class CustomUser(AbstractUser, PermissionsMixin):
    """Custom user model supporting multiple roles."""
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    phone_number = PhoneNumberField(unique=True, region="NG")
    address = models.CharField(max_length = 100)
    password_reset_required = models.BooleanField(default=True)
    first_login = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    user_image = models.ImageField(upload_to='images/user_img')
    create_date = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number"]

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        elif self.email:
            return self.email
        return "Anonymous"
    
class OtpToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6, unique=True, blank=True)
    otp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)

    def generate_unique_otp(self):
        """Generate a unique 6-digit OTP."""
        while True:
            otp = f"{secrets.randbelow(1000000):06d}"  # Ensures a 6-digit OTP
            if not OtpToken.objects.filter(otp_code=otp).exists():
                return otp

    def save(self, *args, **kwargs):
        if not self.otp_code:  # Generate OTP only if it's not already set
            self.otp_code = self.generate_unique_otp()
        super().save(*args, **kwargs)
from django.db import models


CATEGORY_CHOICES = [
    ("appliances", "Appliances"),
    ("phones", "Phones & Tablets"),
    ("health", "Health & Beauty"),
    ("fashion", "Fashion"),
    ("supermarket", "Supermarket"),
    ("computing", "Computing"),
    ("gaming", "Gaming"),
    ("music", "Musical Instruments"),
    ("books", "Books"),
    ("therapy", "Therapeutic Resources"),
    ("others", "Other Categories"),
]


class Category(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name
    
    @property
    def children(self):
        return self.category_set.all()
    
    @property
    def is_root(self):
        return self.parent is None

    def save(self, *args, **kwargs):
        self.slug = slugify(self.slug)
        self.name = dict(CATEGORY_CHOICES).get(self.slug, self.slug.title())
        super().save(*args, **kwargs)


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    def save(self, *args, **kwargs):
        if not self.slug and self.category and self.name:
            self.slug = slugify(f"{self.category.slug}-{self.name}")
        super().save(*args, **kwargs)
        
    class Meta:
        unique_together = ('category', 'name') 


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    STOCK_STATUS = [
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    subcategory = ChainedForeignKey(
        SubCategory,
        chained_field="category",
        chained_model_field="category",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.CASCADE 
        )
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unisex')
    color = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100)
    delivery_time = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    sku = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    tags = TaggableManager()
 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.sku}")
        super().save(*args, **kwargs)

    @property
    def stock_status(self):
        if self.quantity is None:
            return "Unknown" 
        elif self.quantity == 0:
            return 'out_of_stock'
        elif self.quantity < 5:
            return 'low_stock'
        return 'in_stock'

    @property
    def is_available(self):
        if self.quantity is None:
            return False
        return self.quantity > 0
    
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"Cart ({self.user or self.session_key}) - {self.total_items()} items"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot of price at time of addition

    class Meta:
        unique_together = ('cart', 'product')


class GDPRConsent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agreed_to_terms = models.BooleanField(default=False)
    agreed_to_privacy_policy = models.BooleanField(default=False)
    gdpr_consent = models.BooleanField(default=False)
    consent_date = models.DateTimeField(blank = True, null = True)

    def __str__(self):
        return f"{self.user.username} GDPR Consent"

    def set_consent(self):
        """Set the consent flags to True and save the consent date."""
        self.agreed_to_terms = True
        self.agreed_to_privacy_policy = True
        self.consent_date = timezone.now()
        self.save()

    def revoke_consent(self):
        """Revoke consent by setting both flags to False."""
        self.agreed_to_terms = False
        self.agreed_to_privacy_policy = False
        self.consent_date = None
        self.save()
            
class RegistrationProgress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    step = models.IntegerField(default=2)  # Track the current step (2 to 5)
    completed = models.BooleanField(default=False)  # True when 100% complete

    def progress_percentage(self):
        return (self.step / 5) * 100  # Adjust based on the number of steps
# class Product(models.Model):
#     productName = models.CharField(max_length=250)
#     quantity = models.IntegerField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     description=models.CharField(max_length=150)
#     image = models.ImageField(upload_to='images/')
#     stock = models.PositiveIntegerField()
#     quantity = models.IntegerField()
    
#     def __str__(self):
#         return self.productName
    
#     def save(self, *args, **kwargs):
#         # On creation, set stock equal to initial_quantity
#         if not self.pk:  # Check if it's a new instance
#             self.stock = self.quantity
#         else:
#             # For existing products, keep the current stock or update it
#             self.stock += kwargs.pop('add_stock', 0)  # Increment stock if specified

#         super().save(*args, **kwargs)  # Call the original save method
        
#     def is_in_stock(self):
#         return self.stock > 0
#     def get_absolute_url(self):
#         return reverse('home')
    

    
# class CartItem(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)

#     def __str__(self):
#         return f"{self.quantity} of {self.product.productName}"

#     def get_total_price(self):
#         return self.quantity * self.product.price
    
