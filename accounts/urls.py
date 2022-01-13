from django.urls import path
from .views import UserProfileUpdateView


urlpatterns = [
    path('<int:pk>/', UserProfileUpdateView.as_view(), name='user_update'),
]