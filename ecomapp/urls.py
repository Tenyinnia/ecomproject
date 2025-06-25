from django.urls import path
from ecomapp import views
from django.contrib import admin
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

# def superuser_redirect(request):
#     return redirect('admin_superuser')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name = "home"),
    path('register/', views.register_page, name ='register'),
    path('login/', views.user_login, name ='user_login'),
    path('admin/get_subcategories/', views.get_subcategories, name='get_subcategories'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('api/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
    path('my_wishlist/', views.wishlist_view, name='wishlist_view'),

    # path('admin/superuser/', views.SuperuserPageView.as_view(), name='superuser_page'),
    # path('admin/regular/', views.RegularAdminPageView.as_view(), name='regular_admin_page'),
    # path('', views.home, name ='home'),
    # path('product_upload/', views.ProductCreateView.as_view(), name = 'product_upload'),
    # path('about_us/', views.AboutUsView.as_view(), name ='about_us'),
    # path('update/<int:pk>/',views.ProductUpdateView.as_view(), name = 'update'),
    # path('item/<int:pk>/delete/',views.ProductDeleteView.as_view(), name= 'delete'),
    # path('add-to-cart/<int:id>/', views.add_to_cart, name='add-to-cart'),
    # path('signup/', views.signup_view, name='signup'),
    # path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),
    # path('remove-from-cart/<int:id>/', views.remove_from_cart, name='remove-from-cart'),
    
    path('cart/', views.view_cart, name='cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]