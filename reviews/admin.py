from django.contrib import admin
from .models import Review, ReviewReply
# Register your models here.


class ReviewInline(admin.TabularInline):
    model = Review


class ReviewReplyInline(admin.TabularInline):
    model = ReviewReply


class ReviewAdmin(admin.ModelAdmin):
    inlines = [ReviewReplyInline]
    list_display = ('review', 'book', 'author')


admin.site.register(Review, ReviewAdmin)
