from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
# Register your models here.

CustomUser = get_user_model()


class CustomUserAdmin(UserAdmin):
    form = CustomUserCreationForm
    add_form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'is_staff']


admin.sites.register(CustomUser, CustomUserAdmin)
