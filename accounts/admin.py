from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from carts.admin import UserCartInline, UserWishInline
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import UserAddress
# Register your models here.

CustomUser = get_user_model()


class UserAddressInline(admin.TabularInline):
    model = UserAddress


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser
    inlines = [UserAddressInline, UserCartInline, UserWishInline]
    list_display = ['username', 'email', 'is_staff']
    user_fieldsets = UserAdmin.fieldsets
    new_personal_data_fields = user_fieldsets[1][1]['fields'] + ('image', 'phone_number', 'card_number', )
    user_fieldsets[1][1].update(
        {'fields': new_personal_data_fields}
    )
    fieldsets = user_fieldsets


class UserAddressAdmin(admin.ModelAdmin):
    plural_name = 'addresses'


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserAddress, UserAddressAdmin)



