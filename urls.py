from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from shop import consumers
from .views import login_view, checkout_view, add_to_wishlist
from . import views  # Import all views at once

# URL Configuration
urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('add-product/', views.add_product, name='add-product'),
    path('update-product/<int:product_id>/', views.update_product, name='update-product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete-product'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='user_login'),
    path('checkout/', checkout_view, name='checkout'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('save_location/', views.save_location, name='save_location'),
    path('chat/', views.chat_view, name='chat'),
    path('kyc-verification/', views.kyc_verification, name='kyc_verification'),
    path('deals/', views.deals, name='deals'),  # Deals route added
    path('wishlist/', views.wishlist, name='wishlist'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path("checkout/", views.checkout, name="checkout"),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-error/', views.payment_error, name='payment_error'),
    path('update-cart/', views.update_cart, name='update_cart'),
   

]

# WebSocket URLs
websocket_urlpatterns = [
    path('ws/chat/', consumers.ChatConsumer.as_asgi()),
]

# Static & Media Files Handling (only in debug mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
