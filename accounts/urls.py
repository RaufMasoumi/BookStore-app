from django.urls import path
from .views import UserProfileUpdateView, UserProfileDetailView, UserAddressListView, UserAddressUpdateView, UserAddressCreateView, \
    UserAddressDeleteView, UserCartDetailView, UserWishDetailView, user_cart_update_view, user_wish_update_view

urlpatterns = [
    path('', UserProfileDetailView.as_view(), name='account_user_detail'),
    path('<int:pk>/', UserProfileDetailView.as_view(), name='account_user_detail'),
    path('update/', UserProfileUpdateView.as_view(), name='account_user_update'),
    path('<int:pk>/update/', UserProfileUpdateView.as_view(), name='account_user_update'),
    path('addresses/', UserAddressListView.as_view(), name='account_user_address_list'),
    path('<int:user_pk>/addresses/', UserAddressListView.as_view(), name='account_user_address_list'),
    path('addresses/<int:pk>/update/', UserAddressUpdateView.as_view(), name='account_user_address_update'),
    path('addresses/<int:pk>/delete', UserAddressDeleteView.as_view(), name='account_user_address_delete'),
    path('addresses/create/', UserAddressCreateView.as_view(), name='account_user_address_create'),
    path('cart/', UserCartDetailView.as_view(), name='account_user_cart_detail'),
    path('cart/<uuid:pk>/', UserCartDetailView.as_view(), name='account_user_cart_detail'),
    path('cart/update/', user_cart_update_view, name='account_user_cart_update'),
    path('cart/<uuid:pk>/update/', user_cart_update_view, name='account_user_cart_update'),
    path('wishlist/', UserWishDetailView.as_view(), name='account_user_wishlist_detail'),
    path('wishlist/<uuid:pk>/', UserWishDetailView.as_view(), name='account_user_wishlist_detail'),
    path('wishlist/update/', user_wish_update_view, name='account_user_wishlist_update'),
    path('wishlist/<uuid:pk>/update/', user_wish_update_view, name='account_user_wishlist_update'),
]

