# Create your views here.
from ecomapp.models import Product
from django.views.generic import ListView, TemplateView
from django.urls import  reverse, reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Product, CartItem
from django.shortcuts import redirect,render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .mixins import SuperuserRequiredMixin, StaffRequiredMixin

# Superuser view
class SuperuserPageView(SuperuserRequiredMixin, TemplateView):
    template_name = 'admin/superuser_page.html'

# Regular admin view
class RegularAdminPageView(StaffRequiredMixin, TemplateView):
    template_name = 'admin/regular_admin_page.html'

# Admin redirect view
class AdminRedirectView(StaffRequiredMixin, TemplateView):
    template_name = None  # No template for redirect

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect('superuser_page')  # Redirect to superuser page
        return redirect('regular_admin_page')  # Redirect to regular admin page
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')  # Change 'home' to your desired route
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = UserCreationForm()
    return render(request, 'ecomapp/signup.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('home')  # Change 'home' to your desired route
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'ecomapp/login.html', {'form': form})

# Logout View

def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully!')
    return redirect('login')  # Redirect to login page

# Create your views here.
class ProductListView(ListView):
    model=Product
 

class ProductCreateView(PermissionRequiredMixin, CreateView):
    model = Product
    fields=('productName', 'quantity', 'price','description', 'image')
    success_url = reverse_lazy('home')
    permission_required = 'ecomapp.add_product'
    
    def get_permission_denied_message(self):
        return "You don't have permission to add a product"

class AboutUsView(TemplateView):
    template_name = 'ecomapp/about_us.html'
    success_url = reverse_lazy('home')

def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    if not product.is_in_stock():
        return JsonResponse({'error': 'Product is out of stock'}, status=400)

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        # Increment quantity if the item already exists in the cart
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            return JsonResponse({'error': 'Out of stock'}, status=400)

    # Return the updated cart count and stock count
    cart_count = CartItem.objects.filter(user=request.user).count()
    return JsonResponse({'cart_count': cart_count, 'stock': product.stock - cart_item.quantity})

def remove_from_cart(request, id):
    product = get_object_or_404(Product, id=id)
    cart_item = CartItem.objects.filter(user=request.user, product=product).first()
    if cart_item:
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()
    
    cart_count = CartItem.objects.filter(user=request.user).count()
    return JsonResponse({'cart_count': cart_count})

def get_cart_count(request):
    cart_count = CartItem.objects.filter(user=request.user).count()
    return JsonResponse({'cart_count': cart_count})


def cart_view(request):
    # Get cart from session or initialize as empty
    cart = request.session.get('cart', {})
    total_price = sum(int(item['quantity']) * float(item['price']) for item in cart.values())
    
    return render(request, 'ecomapp/cart.html', {'cart': cart, 'total_price': total_price})


class ProductUpdateView(PermissionRequiredMixin, UpdateView):
    model= Product
    fields= ('quantity','price', 'description')
    success_url = reverse_lazy('home')
    permission_required= 'ecomapp.change_product'
    login_url = 'login'

class ProductDeleteView(PermissionRequiredMixin, DeleteView):
    model = Product
    template_name= 'ecomapp/product_confirm_delete.html'
    success_url = reverse_lazy('home')
    permission_required= 'ecomapp.delete_product'
    login_url = 'login'
    #def get_absolute_url(self):
    def get_object(self, queryset=None):
        # Optionally, customize the object retrieval logic
        obj = get_object_or_404(Product, pk=self.kwargs['pk'])
        return obj
        #return redirect('ecomapp/product_confirm_delete.html')