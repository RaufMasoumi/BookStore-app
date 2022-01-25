from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
import uuid
# Create your models here.


class BookManager(models.Manager):

    def published(self):
        return self.filter(status='p')

    def drafted(self):
        return self.filter(status='d')


class Category(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    title = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='categories')
    status = models.BooleanField(default=True, verbose_name='To be displayed?')
    position = models.IntegerField()

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['parent_id', 'position']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'pk': self.pk})


class Book(models.Model):

    STATUS_CHOICES = [
            ('p', 'Published'),
            ('d', 'Draft'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    cover = models.ImageField(upload_to='covers/', blank=True, max_length=200)
    stock = models.PositiveIntegerField(default=0, blank=True)
    buys = models.PositiveIntegerField(default=0, blank=True)
    category = models.ManyToManyField(Category, related_name='books', blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='p')
    objects = BookManager()

    class Meta:
        indexes = [
            models.Index(fields=['id'], name='id_index')
        ]
        permissions = [
            ('special_status', 'Can read all books'),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'pk': self.pk})


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    review = models.CharField(max_length=250)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    submitted = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['submitted']

    def __str__(self):
        return self.review[:20]

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'pk': self.book.pk})


class ReviewReply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='replies')
    reply = models.CharField(max_length=250)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    replied = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'ReviewReplies'
        ordering = ['replied']

    def __str__(self):
        return f'{self.reply[:20]} reply for {self.review}'

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'pk': self.review.book.pk})
