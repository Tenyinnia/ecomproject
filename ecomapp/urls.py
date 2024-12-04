from django.urls import path
from ecomapp import views
from django.contrib import admin
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

def superuser_redirect(request):
    return redirect('admin_superuser')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/superuser/', views.SuperuserPageView.as_view(), name='superuser_page'),
    path('admin/regular/', views.RegularAdminPageView.as_view(), name='regular_admin_page'),
    path('',views.ProductListView.as_view(), name ='home'),
    path('product_upload/', views.ProductCreateView.as_view(), name = 'product_upload'),
    path('about_us/', views.AboutUsView.as_view(), name ='about_us'),
    path('update/<int:pk>/',views.ProductUpdateView.as_view(), name = 'update'),
    path('item/<int:pk>/delete/',views.ProductDeleteView.as_view(), name= 'delete'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add-to-cart'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('remove-from-cart/<int:id>/', views.remove_from_cart, name='remove-from-cart'),
    path('cart-count/', views.get_cart_count, name='cart-count'),
    path('cart/', views.cart_view, name='cart'),
]