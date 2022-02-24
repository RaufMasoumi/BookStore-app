from django.urls import path
from .views import UserProfileUpdateView, UserProfileDetailView, UserCartDetailView, user_cart_update_view


urlpatterns = [
    path('<int:pk>/', UserProfileDetailView.as_view(), name='account_user_detail'),
    path('<int:pk>/update/', UserProfileUpdateView.as_view(), name='account_user_update'),
    path('carts/<uuid:pk>/', UserCartDetailView.as_view(), name='account_user_cart_detail'),
    path('carts/edit/', user_cart_update_view, name='account_user_cart_update'),
]
