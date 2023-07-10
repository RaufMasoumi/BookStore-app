from django.db import models
from django.urls import reverse
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from categories.models import Category
from accounts.models import CustomUser
import uuid
# Create your models here.


class BookManager(models.Manager):

    def published(self):
        return self.filter(status='p')

    def draft(self):
        return self.filter(status='d')

    def available(self):
        return self.filter(stock__gt=0, status='p')

    def unavailable(self):
        return self.filter(stock__lt=1, status='p')

    def bestseller(self):
        return self.filter(bestseller=True, status='p')

    def new(self):
        return self.filter(new=True, status='p')

    def sale(self):
        return self.filter(sale=True, status='p')

    def mostpopular(self):
        return self.filter(mostpopular=True, status='p')


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
    sale = models.BooleanField(default=False, blank=True, verbose_name='Set as a sale book?(will show in sale products)')
    bestseller = models.BooleanField(default=False, blank=True, verbose_name='Set as a bestseller book?(will show in bestseller products)')
    mostpopular = models.BooleanField(default=False, blank=True, verbose_name='Set as a mostpopular book?(will show in mostpopular products)')
    new = models.BooleanField(default=False, blank=True, verbose_name='Set as a newarrival book?(will show in newarrival products)')
    cover = models.ImageField(default='books/covers/unknownbook.png', upload_to='books/covers/', blank=True, max_length=300)
    pages = models.PositiveIntegerField(default=0, blank=True)
    subject = models.CharField(max_length=50, blank=True, null=True)
    rating = models.FloatField(default=0, blank=True)
    publisher = models.CharField(max_length=200, blank=True, null=True)
    age_range = models.CharField(max_length=100, blank=True, null=True)
    grade_range = models.CharField(max_length=100, blank=True, null=True)
    page_size = models.CharField(max_length=10, blank=True, null=True, verbose_name='page size(like A4)')
    length = models.FloatField(blank=True, null=True, verbose_name='length(cm)')
    width = models.FloatField(blank=True, null=True, verbose_name='width(cm)')
    summary = models.TextField(blank=True, null=True)
    time_to_sell = models.DateTimeField(auto_now_add=True, editable=False)
    stock = models.PositiveIntegerField(default=0, blank=True)
    buys = models.PositiveIntegerField(default=0, blank=True)
    views = models.PositiveIntegerField(default=0, blank=True, null=True)
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
        path_name = 'book_detail' if self.status == 'p' else 'draft_book_detail'
        return reverse(path_name, kwargs={'pk': self.pk})

    def is_available(self):
        return True if self.stock > 0 else False

    def is_published(self):
        return True if self.status == 'p' else False

    def is_in_cart(self, user: CustomUser):
        if user.is_authenticated:
            return user.cart.books.filter(pk=self.pk).exists()
        return False


class BookImage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='books/images/', max_length=300, blank=True)

    def __str__(self):
        return f'{self.book}\'s image'

    def get_absolute_url(self):
        return self.book.get_absolute_url()


@receiver(m2m_changed, sender=Book.category.through)
def update_book_category(instance, action, pk_set,  **kwargs):
    if action == 'post_add':
        pk_list = list(pk_set)
        for pk in pk_list:
            category = Category.objects.get(pk=pk)
            update_book_category_with_category(instance, category)
        instance.save()


def update_book_category_with_category(instance, category):
    category_parent = category.parent
    while category_parent:
        instance.category.add(category_parent)
        category_parent = category_parent.parent
    return instance
