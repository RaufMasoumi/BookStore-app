from django.urls import path
from .views import UserProfileUpdateView, UserProfileDetailView, UserAddressListView, UserAddressUpdateView, UserAddressCreateView, \
    UserAddressDeleteView

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
]

