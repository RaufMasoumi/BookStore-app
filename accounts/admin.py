from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import UserCart, UserWish, UserCartBooksNumber
# Register your models here.

CustomUser = get_user_model()


class UserCartInline(admin.TabularInline):
    model = UserCart


class UserWishInline(admin.TabularInline):
    model = UserWish


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser
    inlines = [UserCartInline, UserWishInline]
    list_display = ['username', 'email', 'is_staff']
    user_fieldsets = UserAdmin.fieldsets
    user_fieldsets[1][1].update(
        {'fields': user_fieldsets[1][1]['fields'] + ('image', 'phone_number', 'address', 'card_number', )}
    )
    fieldsets = user_fieldsets


admin.site.register(CustomUser, CustomUserAdmin)


class UserCartAdmin(admin.ModelAdmin):
    fields = ['user', 'cart']


admin.site.register(UserCart, UserCartAdmin)
admin.site.register(UserWish)
admin.site.register(UserCartBooksNumber)


