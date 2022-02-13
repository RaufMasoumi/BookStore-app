from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
# Create your models here.


class CategoryManager(models.Manager):

    def active(self):
        return self.filter(status=True)


class BookManager(models.Manager):

    def published(self):
        return self.filter(status='p')

    def drafted(self):
        return self.filter(status='d')

    def bestseller(self):
        return self.filter(bestseller=True)

    def new(self):
        return self.filter(new=True)

    def sale(self):
        return self.filter(sale=True)

    def mostpopular(self):
        return self.filter(mostpopular=True)


class Category(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    title = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='categories', blank=True)
    status = models.BooleanField(default=True, verbose_name='To be displayed?', blank=True)
    position = models.IntegerField()
    objects = CategoryManager()

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['parent_id', 'position']

    def get_available_books(self):
        return self.books.filter(stock__gt=0)

    def get_unavailable_books(self):
        return self.books.filter(stock__lt=1)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_books_list', kwargs={'pk': self.pk})


class Book(models.Model):

    STATUS_CHOICES = [
            ('p', 'Published'),
            ('d', 'Draft'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    off = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    sale = models.BooleanField(default=False, blank=True)
    bestseller = models.BooleanField(default=False, blank=True)
    mostpopular = models.BooleanField(default=False, blank=True)
    new = models.BooleanField(default=False, blank=True)
    cover = models.ImageField(upload_to='books/covers/', blank=True, max_length=200)
    pages = models.PositiveIntegerField(default=0, blank=True)
    subject = models.CharField(max_length=50, blank=True, null=True)
    rating = models.FloatField(default=0, blank=True)
    publisher = models.CharField(max_length=200, blank=True, null=True)
    age_range = models.CharField(max_length=100, blank=True, null=True)
    grade_range = models.CharField(max_length=100, blank=True, null=True)
    page_size = models.CharField(max_length=10, blank=True, null=True)
    length = models.FloatField(blank=True, null=True, verbose_name='length(cm)')
    width = models.FloatField(blank=True, null=True, verbose_name='width(cm)')
    summary = models.TextField(blank=True, null=True)
    time_to_sell = models.DateTimeField(auto_now_add=True, editable=False)
    stock = models.PositiveIntegerField(default=0, blank=True)
    buys = models.PositiveIntegerField(default=0, blank=True)
    category = models.ManyToManyField(Category, related_name='books', blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='p', blank=True)
    objects = BookManager()

    class Meta:
        indexes = [
            models.Index(fields=['id'], name='id_index')
        ]
        permissions = [
            ('special_status', 'Can read all books'),
        ]
        ordering = [
            '-time_to_sell',
            'stock'
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.status == 'p':
            return reverse('book_detail', kwargs={'pk': self.pk})
        else:
            return reverse('draft_book_detail', kwargs={'pk': self.pk})


class BookImage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='books/images/', max_length=200, blank=True)

    def __str__(self):
        return f'{self.book}\'s image'

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'pk': self.book.pk})


class Review(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    review = models.CharField(max_length=250)
    rating = models.FloatField(default=0, blank=True)
    submitted = models.DateTimeField(auto_now_add=True, editable=False)
    votes = models.IntegerField(default=0)

    class Meta:
        ordering = ['-submitted']

    def __str__(self):
        return self.review[:20]

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'pk': self.book.pk})


class ReviewReply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='replies')
    reply = models.CharField(max_length=250)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    add = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='add_replies')
    replied = models.DateTimeField(auto_now_add=True)
    votes = models.IntegerField(default=0)

    class Meta:
        ordering = ['replied']
        verbose_name_plural = 'ReviewReplies'

    def __str__(self):
        return f'{self.reply[:20]} reply for {self.review}'

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'pk': self.review.book.pk})


@receiver(post_save, sender=Review)
def update_book_rating(instance, **kwargs):
    book = instance.book
    ratings = [review.rating for review in book.reviews.all()]
    ave_rating = sum(ratings) / book.reviews.count()
    book.rating = round(ave_rating, 1)
    book.save()
    return
