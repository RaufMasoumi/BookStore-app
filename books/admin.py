from django.contrib import admin
from .models import Book, BookImage, Category, Review, ReviewReply
# Register your models here.


class ReviewInline(admin.TabularInline):
    model = Review


class BookImageInline(admin.StackedInline):
    model = BookImage


class BookAdmin(admin.ModelAdmin):
    inlines = [BookImageInline, ReviewInline]
    list_display = ('title', 'author', 'price', 'sale')


admin.site.register(Book, BookAdmin)


class BookImageAdmin(admin.ModelAdmin):
    list_display = ('book',)


admin.site.register(BookImage, BookImageAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent')


admin.site.register(Category, CategoryAdmin)


class ReviewReplyInline(admin.TabularInline):
    model = ReviewReply


class ReviewAdmin(admin.ModelAdmin):
    inlines = [ReviewReplyInline]
    list_display = ('review', 'book', 'author')


admin.site.register(Review, ReviewAdmin)
