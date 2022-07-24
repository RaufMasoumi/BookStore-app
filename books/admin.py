from django.contrib import admin
from reviews.admin import ReviewInline
from .models import Book, BookImage
# Register your models here.


class BookImageInline(admin.StackedInline):
    model = BookImage


@admin.action(description='Mark selected books as published')
def make_published(modeladmin, request, queryset):
    return queryset.update(status='p')


@admin.action(description='Mark selected books as draft')
def make_draft(modeladmin, request, queryset):
    return queryset.update(status='d')


@admin.action(description='Mark selected books as sale')
def make_sale(modeladmin, request, queryset):
    return queryset.update(sale=True)


@admin.action(description='Mark selected books as new')
def make_new(modeladmin, request, queryset):
    return queryset.update(new=True)


@admin.action(description='Mark selected books as bestseller')
def make_bestseller(modeladmin, request, queryset):
    return queryset.update(bestseller=True)


@admin.action(description='Mark selected books as mostpopular')
def make_mostpopular(modeladmin, request, queryset):
    return queryset.update(mostpopular=True)


class BookAdmin(admin.ModelAdmin):
    inlines = [BookImageInline, ReviewInline]
    list_display = ['title', 'author', 'price', 'status']
    actions = [make_new, make_sale, make_bestseller, make_mostpopular, make_draft, make_published]


admin.site.register(Book, BookAdmin)


class BookImageAdmin(admin.ModelAdmin):
    list_display = ('book',)


admin.site.register(BookImage, BookImageAdmin)
