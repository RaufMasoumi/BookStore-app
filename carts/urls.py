from django.urls import path
from .views import UserCartDetailView, user_cart_update_view, UserWishDetailView, user_wish_update_view

urlpatterns = [
    path('', UserCartDetailView.as_view(), name='account_user_cart_detail'),
    path('<uuid:pk>/', UserCartDetailView.as_view(), name='account_user_cart_detail'),
    path('update/', user_cart_update_view, name='account_user_cart_update'),
    path('<uuid:pk>/update/', user_cart_update_view, name='account_user_cart_update'),
    path('wishlist/', UserWishDetailView.as_view(), name='account_user_wishlist_detail'),
    path('wishlist/<uuid:pk>/', UserWishDetailView.as_view(), name='account_user_wishlist_detail'),
    path('wishlist/update/', user_wish_update_view, name='account_user_wishlist_update'),
    path('wishlist/<uuid:pk>/update/', user_wish_update_view, name='account_user_wishlist_update'),
]
