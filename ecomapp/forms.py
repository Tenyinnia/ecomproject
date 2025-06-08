from django import forms
from .models import Product
from django.forms import ModelForm
from ecomapp.validators import CustomPasswordValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from django.core.exceptions import ValidationError
from ecomapp.validators import CustomPasswordValidator
from .models import CustomUser, GDPRConsent
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .password_blacklist import is_common_password
import os
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import RegionalPhoneNumberWidget
from django.core.validators import RegexValidator
from django.forms.widgets import DateInput, FileInput, TextInput, Select
import random
import string
from django.core.mail import send_mail
from django.utils.text import slugify
from .models import Product, Category, SubCategory, Brand

#class ComplainForm(ModelForm):
    
    # class Meta:
    #     model = Product
    #     fields=('productName', 'quantity', 'price','description','productTypes', 'image')
    #     #fields = ['name', 'quantity', 'supplier', 'comment', 'gender', 'uploads']
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15, required=True)
    class Meta:
        model = get_user_model()
        fields = ['username','first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2']
        
    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        validator = CustomPasswordValidator()
        validator.validate(password)  # Apply validation rules
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match")
        return cleaned_data 
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("Phone number is already in use.")
        return phone_number

class UserAddressForm(forms.ModelForm):
    class Meta:
        model:CustomUser
        fields = ["address"] 
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Home Address'}),
        }  
# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = [
#             'name', 'category', 'description', 'price',
#             'discounted_price', 'quantity', 'sku', 'image', 'is_available'
#         ]
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 4}),
#             'price': forms.NumberInput(attrs={'step': '0.01'}),
#             'discounted_price': forms.NumberInput(attrs={'step': '0.01'}),
#             'quantity': forms.NumberInput(attrs={'min': '0'}),
#        


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter product name',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Enter detailed product description',
                'rows': 4,
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'class': 'form-control'
            }),
            'discounted_price': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'class': 'form-control'
            }),
            'quantity': forms.NumberInput(attrs={
                'min': '0',
                'class': 'form-control'
            }),
            'delivery_time': forms.TextInput(attrs={
                'placeholder': 'e.g., 3-5 business days',
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'file-input',
                'onchange': 'updateFileName(this)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields not required
        self.fields['discounted_price'].required = False
        self.fields['brand'].required = False
        self.fields['subcategory'].required = False
        self.fields['image'].required = False
        self.fields['color'].required = False
        
        # Add class to all fields
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
        
        # Dynamic subcategory filtering
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = SubCategory.objects.filter(category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category:
            self.fields['subcategory'].queryset = self.instance.category.subcategories.order_by('name')
        else:
            self.fields['subcategory'].queryset = SubCategory.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        discounted_price = cleaned_data.get('discounted_price')
        
        if discounted_price and price and discounted_price >= price:
            raise forms.ValidationError(
                "Discounted price must be lower than regular price"
            )
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(f"{instance.name}-{instance.sku}")
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control'}),
            'icon': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            return slugify(slug)
        return slug


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = '__all__'
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all().order_by('name')


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }