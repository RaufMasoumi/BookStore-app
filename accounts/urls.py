from django.urls import path
from .views import UserProfileUpdateView, UserCartDetailView, user_cart_update_view


urlpatterns = [
    path('<int:pk>/', UserProfileUpdateView.as_view(), name='account_user_update'),
    path('carts/<uuid:pk>/', UserCartDetailView.as_view(), name='account_user_cart_detail'),
    path('carts/edit/', user_cart_update_view, name='account_user_cart_update'),
]
