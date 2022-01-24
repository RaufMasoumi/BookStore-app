from django.contrib import admin
from .models import Book, Review, ReviewReply
# Register your models here.


class ReviewInline(admin.TabularInline):
    model = Review


class BookAdmin(admin.ModelAdmin):
    inlines = [ReviewInline]
    list_display = ('title', 'author', 'price',)


admin.site.register(Book, BookAdmin)


class ReviewReplyInline(admin.TabularInline):
    model = ReviewReply


class ReviewAdmin(admin.ModelAdmin):
    inlines = [ReviewReplyInline]
    list_display = ('review', 'book', 'author')


admin.site.register(Review, ReviewAdmin)
