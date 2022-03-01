from django.urls import path
from .views import UserProfileUpdateView, UserProfileDetailView, UserCartDetailView, UserWishDetailView,\
    user_cart_update_view, user_wish_update_view


urlpatterns = [
    path('', UserProfileDetailView.as_view(), name='account_user_detail'),
    path('update/', UserProfileUpdateView.as_view(), name='account_user_update'),
    path('cart/', UserCartDetailView.as_view(), name='account_user_cart_detail'),
    path('cart/<uuid:pk>/', UserCartDetailView.as_view(), name='account_user_cart_detail'),
    path('cart/edit/', user_cart_update_view, name='account_user_cart_update'),
    path('cart/<uuid:pk>/edit/', user_cart_update_view, name='account_user_cart_update'),
    path('wishlist/', UserWishDetailView.as_view(), name='account_user_wishlist_detail'),
    path('wishlist/<uuid:pk>/', UserWishDetailView.as_view(), name='account_user_wishlist_detail'),
    path('wishlist/edit/', user_wish_update_view, name='account_user_wishlist_update'),
    path('wishlist/<uuid:pk>/edit/', user_wish_update_view, name='account_user_wishlist_update'),
]

