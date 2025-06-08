# # Create your views here.
from django.views.generic import ListView, TemplateView
from django.urls import  reverse, reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Product #CartItem
from django.shortcuts import redirect,render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .mixins import SuperuserRequiredMixin, StaffRequiredMixin
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import generics
from .models import CustomUser
from .serializers import CustomUserSerializer
from .forms import RegisterForm
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import OtpToken
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import authenticate, get_backends, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .mixins import SuperuserRequiredMixin, StaffRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, TemplateView, FormView
#from .forms import RegisterForm
from urllib.parse import urlparse, urlunparse
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm,PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
# UserModel = get_user_model()
from django.contrib.auth.views import LoginView, PasswordResetView
from django.urls import reverse_lazy
from django.db.models import Case, When, Value, BooleanField
from django.contrib.messages import get_messages
from ecomapp.authentication import EmailAuthBackend
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .models import RegistrationProgress, GDPRConsent, OtpToken, Cart, CartItem
from rest_framework.views import APIView
from rest_framework import status
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
from django.db import transaction
def home(request):
    category_slug = request.GET.get('category')
    subcategory_slug = request.GET.get('subcategory')
    brand_slug = request.GET.get('brand')
    gender = request.GET.get('gender')
    tag_slug = request.GET.get('tag')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    query = request.GET.get('query')
    sort = request.GET.get('sort', 'newest')
    
    # Base queryset
    products = Product.objects.filter(quantity__gt=0)
    # Apply filters
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
        
    if subcategory_slug:
        subcategory = get_object_or_404(SubCategory, slug=subcategory_slug)
        products = products.filter(subcategory=subcategory)
        
    if brand_slug:
        brand = get_object_or_404(Brand, slug=brand_slug)
        products = products.filter(brand=brand)
        
    if gender:
        products = products.filter(gender=gender)
        
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])
        
    if min_price:
        products = products.filter(price__gte=min_price)
        
    if max_price:
        products = products.filter(price__lte=max_price)
        
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    # Apply sorting
    if sort == 'popular':
        products = products.annotate(num_orders=Count('order_items')).order_by('-num_orders')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'discount':
        products = products.exclude(discounted_price__isnull=True).order_by('-discounted_price')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 24)  # 24 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options for sidebar
    categories = Category.objects.annotate(product_count=Count('product'))
    brands = Brand.objects.annotate(product_count=Count('product')).order_by('name')
    tags = Tag.objects.all()[:20]  # Top 20 tags
    
    # Get counts for gender filter
    gender_counts = {
        'women': products.filter(gender='female').count(),
        'men': products.filter(gender='male').count(),
        'unisex': products.filter(gender='unisex').count(),
    }
    
    # Get price range
    price_range = products.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    context = {
        
        'products': page_obj,
        'categories': categories,
        'brands': brands,
        'tags': tags,
        'current_category': get_object_or_404(Category, slug=category_slug) if category_slug else None,
        'current_subcategory': get_object_or_404(SubCategory, slug=subcategory_slug) if subcategory_slug else None,
        'women_count': gender_counts['women'],
        'men_count': gender_counts['men'],
        'unisex_count': gender_counts['unisex'],
        'query': query,
        'min_price': price_range['min_price'],
        'max_price': price_range['max_price'],
    }
    return render(request, "ecomapp/index.html", context)

class RegisterUserAPIView(viewsets.ModelViewSet):
    queryset=CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    
    @action(detail=False, methods=['post'])
    def create_user(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

#CBV Serializer
# class RegisterUserView(generics.CreateAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = CustomUserSerializer
def register_page(request):
    return render(request, 'ecomapp/signup.html')

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # Custom action to create a new product from frontend
    @action(detail=False, methods=['post'])
    def create_product(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.data)
        if form.is_valid():
            # Serialize the data using the CustomUserSerializer
            serializer = CustomUserSerializer(data=form.cleaned_data)
            if serializer.is_valid():
                user = serializer.save()
                return JsonResponse({"message": "User registered successfully!"}, status=201)
            return JsonResponse(serializer.errors, status=400)
        else:
            return JsonResponse(form.errors, status=400)

    return JsonResponse({"message": "Invalid request method."}, status=400)

# def register(request):
#     if request.method == "POST":
#         form = RegisterForm(request.POST)
        
#         if form.is_valid():
#             email = form.cleaned_data["email"]
#             username = form.cleaned_data["username"]

#             # Check if email is already in use
#             if get_user_model().objects.filter(email=email).exists():
#                 messages.error(request, 'User with this email already exists.')
#             else:
#                 user = form.save(commit=False)
#                 user.set_password(form.cleaned_data["password1"])  # Hash password
#                 user.save()
                
#                 messages.success(request, 'Account created successfully! An OTP was sent to your email')
#                 return redirect('verify_email', username=username)
#         else:
#             messages.error(request, form.errors)  # Show form errors

#     else:
#         form = RegisterForm()

#     return render(request, 'lmsApp/registration/signup.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'Logged out successfully!')
    return redirect('user_login')


User = get_user_model()

def user_login(request):
    if request.user.is_authenticated:
        # Fetch or create the user's progress tracker
        tracker, created = RegistrationProgress.objects.get_or_create(user=request.user)

        # Redirect to the last step they were on
        if tracker.step < 5:  # Ensure they haven't completed all steps
            return redirect("profile_completion")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")
        user = EmailAuthBackend().authenticate(request, email=email, password=password)

        if user is not None:
            user.backend = "lmsApp.authentication.EmailAuthBackend"
            login(request, user)
            messages.success(request, "Login successful!")

            # request.session.set_expiry(0)  # Keeps session alive while browser is open
            # request.session.modified = True  # Ensure session updates
            if remember_me:
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
            else:
                request.session.set_expiry(0)  # Expires when browser closes

            # Fetch or create step tracker
            tracker, created = RegistrationProgress.objects.get_or_create(user=user)

            # Redirect based on user type
            if user.is_superuser:
                return redirect("admin:index")
            elif user.is_staff:
                return redirect("product_owner_dashboard")
            elif user.user_type and user.user_type.strip().lower() == "hr":
                return redirect("hr_dashboard")
            elif user.user_type and user.user_type.strip().lower() == "student":
                if tracker.step > 2: # Ensure they haven't completed all steps
                    return redirect("student_dashboard")
                else:# Ensure session persists
                    return redirect("student_registration")
            elif user.user_type and user.user_type.strip().lower() == "tutor":
                # Redirect tutors to the last form step they were on
                if tracker.step < 5:  # Ensure they haven't completed all steps
                    return redirect("profile_completion")
                else:
                    return redirect("tutor_dashboard")
            else:
                messages.error(request, "User type not recognized.")
                return redirect("user_login")

        else:
            messages.error(request, "Invalid email or password. Please try again.")
            return redirect("user_login")

    return render(request, "ecomapp/login.html")

def verify_email(request, username):
    user = get_user_model().objects.get(username = username)
    user_otp = OtpToken.objects.filter(user = user).last()
    if request.method == "POST":
        if user_otp.otp_code == request.POST["otp_code"]:
            if user_otp.otp_expires_at > timezone.now():
                user.is_active = True
                user.save()
                messages.success(request, "Account created successfully! You can login to complete your profile")
                return redirect("user_login")
            else:
                messages.warning(request, "The OTP has expired, get a new OTP")
                return redirect("verify_email", username = user.username)
        else:
            messages.warning(request, "Invalid OTP entered. Enter a valid OTP")
            return redirect("verify_email", username = user.username)
        
    context = {}
    return render(request, "lmsApp/verify_token.html", context)

def resend_otp(request):
    if request.method == "POST":
        user_email = request.POST.get("otp_email")
        if get_user_model().objects.filter(email = user_email).exists():
            user = get_user_model().objects.get(email= user_email)
            otp = OtpToken.objects.create(user=user, otp_expires_at = timezone.now() + timezone.timedelta(minutes = 5))
            subject = "Email Verification"
            message = f"""
                        Hi {user.username}, here is your otp {otp.otp_code}
                        It expires in 5 minutes, use the url below to redirect back 
                        to the website to complete your registration.
                        
                        http://127.0.0.1:8000/verify_email/{user.username}
                    """
            sender = "smartlearnk12@gmail.com"
            receiver = [user.email, ]
        
            send_mail (
                subject,
                message,
                sender,
                receiver,
                fail_silently=False
            )
            messages.success(request, "A new OTP has been sent to your email address")
            return redirect("verify_email", username = user.username)
        else:
            messages.warning(request, "The email does not exist in the database.")
            return redirect("resend_otp")
    context = {}
    return render(request, "lmsApp/resend_otp.html", context)  
# # Superuser view
# class SuperuserPageView(SuperuserRequiredMixin, TemplateView):
#     template_name = 'admin/superuser_page.html'

# # Regular admin view
# class RegularAdminPageView(StaffRequiredMixin, TemplateView):
#     template_name = 'admin/regular_admin_page.html'

# # Admin redirect view
# class AdminRedirectView(StaffRequiredMixin, TemplateView):
#     template_name = None  # No template for redirect

#     def get(self, request, *args, **kwargs):
#         if request.user.is_superuser:
#             return redirect('superuser_page')  # Redirect to superuser page
#         return redirect('regular_admin_page')  # Redirect to regular admin page
# def signup_view(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             messages.success(request, 'Account created successfully!')
#             return redirect('home')  # Change 'home' to your desired route
#         else:
#             messages.error(request, 'Invalid form submission.')
#     else:
#         form = UserCreationForm()
#     return render(request, 'ecomapp/signup.html', {'form': form})

# # Login View
# def login_view(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             messages.success(request, 'Logged in successfully!')
#             return redirect('home')  # Change 'home' to your desired route
#         else:
#             messages.error(request, 'Invalid username or password.')
#     else:
#         form = AuthenticationForm()
#     return render(request, 'ecomapp/login.html', {'form': form})

# # Logout View

# def logout_view(request):
#     logout(request)
#     messages.info(request, 'Logged out successfully!')
#     return redirect('login')  # Redirect to login page

# # Create your views here.
# class ProductListView(ListView):
#     model=Product
 

# class ProductCreateView(PermissionRequiredMixin, CreateView):
#     model = Product
#     fields=('productName', 'quantity', 'price','description', 'image')
#     success_url = reverse_lazy('home')
#     permission_required = 'ecomapp.add_product'
    
#     def get_permission_denied_message(self):
#         return "You don't have permission to add a product"

# class AboutUsView(TemplateView):
#     template_name = 'ecomapp/about_us.html'
#     success_url = reverse_lazy('home')

# def add_to_cart(request, id):
#     product = get_object_or_404(Product, id=id)
#     if not product.is_in_stock():
#         return JsonResponse({'error': 'Product is out of stock'}, status=400)

#     cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
#     if not created:
#         # Increment quantity if the item already exists in the cart
#         if cart_item.quantity < product.stock:
#             cart_item.quantity += 1
#             cart_item.save()
#         else:
#             return JsonResponse({'error': 'Out of stock'}, status=400)

#     # Return the updated cart count and stock count
#     cart_count = CartItem.objects.filter(user=request.user).count()
#     return JsonResponse({'cart_count': cart_count, 'stock': product.stock - cart_item.quantity})

# def remove_from_cart(request, id):
#     product = get_object_or_404(Product, id=id)
#     cart_item = CartItem.objects.filter(user=request.user, product=product).first()
#     if cart_item:
#         cart_item.quantity -= 1
#         if cart_item.quantity <= 0:
#             cart_item.delete()
#         else:
#             cart_item.save()
    
#     cart_count = CartItem.objects.filter(user=request.user).count()
#     return JsonResponse({'cart_count': cart_count})

# def get_cart_count(request):
#     cart_count = CartItem.objects.filter(user=request.user).count()
#     return JsonResponse({'cart_count': cart_count})


# def cart_view(request):
#     # Get cart from session or initialize as empty
#     cart = request.session.get('cart', {})
#     total_price = sum(int(item['quantity']) * float(item['price']) for item in cart.values())
    
#     return render(request, 'ecomapp/cart.html', {'cart': cart, 'total_price': total_price})


# class ProductUpdateView(PermissionRequiredMixin, UpdateView):
#     model= Product
#     fields= ('quantity','price', 'description')
#     success_url = reverse_lazy('home')
#     permission_required= 'ecomapp.change_product'
#     login_url = 'login'

# class ProductDeleteView(PermissionRequiredMixin, DeleteView):
#     model = Product
#     template_name= 'ecomapp/product_confirm_delete.html'
#     success_url = reverse_lazy('home')
#     permission_required= 'ecomapp.delete_product'
#     login_url = 'login'
#     #def get_absolute_url(self):
#     def get_object(self, queryset=None):
#         # Optionally, customize the object retrieval logic
#         obj = get_object_or_404(Product, pk=self.kwargs['pk'])
#         return obj
#         #return redirect('ecomapp/product_confirm_delete.html')
# def home(request):
#     return render (request, 'highSchoolApp/base.html')
@transaction.atomic
def add_to_cart(request):
    if request.method == 'POST':
        try:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            
            # Get product (or return 404 if not found)
            product = Product.objects.get(id=product_id)
            
            # Add to cart (example logic)
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart.items.add(product, through_defaults={'quantity': quantity})
            
            return JsonResponse({
                'success': True,
                'message': 'Product added to cart!',
                'cart_total': cart.total_items(),
            })
        
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def create_product(request):
    if request.method == 'POST':
        product = Product.objects.create(
            name=request.POST['name'],
            category_id=request.POST['category'],
            price=request.POST['price'],
            description=request.POST['description'],
            quantity=request.POST['quantity'],
        )
        product.tags.add("new", "featured", "hot-sale")
        
from django.http import JsonResponse
from .models import SubCategory

def get_subcategories(request):
    category_id = request.GET.get('category_id')
    if category_id:
        subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
        return JsonResponse({'subcategories': list(subcategories)})
    return JsonResponse({'subcategories': []})


def product_list(request):
    # Get all filter parameters from request
    category_slug = request.GET.get('category')
    subcategory_slug = request.GET.get('subcategory')
    brand_slug = request.GET.get('brand')
    gender = request.GET.get('gender')
    tag_slug = request.GET.get('tag')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    query = request.GET.get('query')
    sort = request.GET.get('sort', 'newest')
    
    # Base queryset
    products = Product.objects.filter(quantity__gt=0)
    # Apply filters
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
        
    if subcategory_slug:
        subcategory = get_object_or_404(SubCategory, slug=subcategory_slug)
        products = products.filter(subcategory=subcategory)
        
    if brand_slug:
        brand = get_object_or_404(Brand, slug=brand_slug)
        products = products.filter(brand=brand)
        
    if gender:
        products = products.filter(gender=gender)
        
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])
        
    if min_price:
        products = products.filter(price__gte=min_price)
        
    if max_price:
        products = products.filter(price__lte=max_price)
        
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    # Apply sorting
    if sort == 'popular':
        products = products.annotate(num_orders=Count('order_items')).order_by('-num_orders')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'discount':
        products = products.exclude(discounted_price__isnull=True).order_by('-discounted_price')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 24)  # 24 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options for sidebar
    categories = Category.objects.annotate(product_count=Count('product'))
    brands = Brand.objects.annotate(product_count=Count('product')).order_by('name')
    tags = Tag.objects.all()[:20]  # Top 20 tags
    
    # Get counts for gender filter
    gender_counts = {
        'women': products.filter(gender='female').count(),
        'men': products.filter(gender='male').count(),
        'unisex': products.filter(gender='unisex').count(),
    }
    
    # Get price range
    price_range = products.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    context = {
        'products': page_obj,
        'categories': categories,
        'brands': brands,
        'tags': tags,
        'current_category': get_object_or_404(Category, slug=category_slug) if category_slug else None,
        'current_subcategory': get_object_or_404(SubCategory, slug=subcategory_slug) if subcategory_slug else None,
        'women_count': gender_counts['women'],
        'men_count': gender_counts['men'],
        'unisex_count': gender_counts['unisex'],
        'query': query,
        'min_price': price_range['min_price'],
        'max_price': price_range['max_price'],
    }
    
    return render(request, 'ecomapp/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(
        Q(category=product.category) |
        Q(subcategory=product.subcategory) |
        Q(brand=product.brand)
    ).exclude(id=product.id).distinct()[:8]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    
    return render(request, 'ecomapp/product_details.html', context)