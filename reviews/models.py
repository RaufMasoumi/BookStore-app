from django.db import models
from django.db.models.signals import pre_save, post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from books.models import Book
# Create your models here.


class Review(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(default='guest', max_length=50, blank=True)
    email = models.EmailField(blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField(max_length=250)
    rating = models.FloatField(default=0, blank=True)
    submitted = models.DateTimeField(auto_now_add=True, editable=False)
    votes = models.IntegerField(default=0, blank=True)

    class Meta:
        ordering = ['votes', '-submitted']

    def __str__(self):
        return f'{self.review[:20]}...'

    def get_absolute_url(self):
        return self.book.get_absolute_url()


class ReviewReply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    to = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')
    name = models.CharField(default='guest', max_length=50, blank=True)
    email = models.EmailField(blank=True)
    reply = models.CharField(max_length=250)
    replied = models.DateTimeField(auto_now_add=True, editable=False)
    votes = models.IntegerField(default=0)

    class Meta:
        ordering = ['votes', '-replied']
        verbose_name_plural = 'Review Replies'

    def __str__(self):
        return f'{self.reply[:20]}... reply for {self.review}...'

    def get_absolute_url(self):
        return self.review.get_absolute_url()


@receiver(post_save, sender=Review)
def update_book_rating(instance, created, **kwargs):
    if created:
        book = instance.book
        ratings = [review.rating for review in book.reviews.all()]
        ave_rating = sum(ratings) / len(ratings)
        book.rating = round(ave_rating, 1)
        book.save()


@receiver(pre_save, sender=Review)
def update_review_name_and_email_by_user(instance, **kwargs):
    user = instance.author
    if user:
        instance.name = user.username
        instance.email = user.email


@receiver(pre_save, sender=ReviewReply)
def update_review_reply_name_and_email_by_user(instance, **kwargs):
    user = instance.author
    if user:
        instance.name = user.username
        instance.email = user.email
