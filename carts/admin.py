from django.contrib import admin
from .models import UserCart, UserCartBooksNumber, UserWish
# Register your models here.


class UserCartInline(admin.TabularInline):
    model = UserCart


class UserWishInline(admin.TabularInline):
    model = UserWish


admin.site.register(UserCart)
admin.site.register(UserWish)
admin.site.register(UserCartBooksNumber)