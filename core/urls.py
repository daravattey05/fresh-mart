from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from . import api_views

app_name = 'core'

router = DefaultRouter()
router.register(r'products', api_views.ProductViewSet, basename='product')
router.register(r'blogs', api_views.BlogViewSet, basename='blog')
router.register(r'orders', api_views.OrderViewSet, basename='order')

urlpatterns = [
    # Web Views
    path('', views.index, name='index'),
    path('shop/', views.shop_grid, name='shop'),
    path('shop/category/<slug:category_slug>/', views.shop_grid, name='shop_by_category'),
    path('product/<slug:slug>/', views.shop_details, name='product_detail'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_details, name='blog_detail'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('khqr-payment/<int:order_id>/', views.khqr_payment, name='khqr_payment'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    
    # API Routes
    path('api/', include(router.urls)),
    path('api/token-auth/', obtain_auth_token, name='api_token_auth'),
]
