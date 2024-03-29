from django.db import models
from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.forms import ValidationError
from books.models import Book
from decimal import Decimal
import uuid
# Create your models here.


class UserCart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='cart')
    books = models.ManyToManyField(Book, related_name='in_carts', blank=True)

    def calculate_total_price(self):
        total_price = Decimal('00.00')
        for book in self.books.all():
            price = book.off if book.off else book.price
            number = UserCartBooksNumber.objects.get(cart=self, book=book).number
            total_price += price * number
        return total_price

    def calculate_total_price_with_cost(self):
        total_price = self.calculate_total_price()
        total_price_with_cost = total_price + 3
        return total_price_with_cost

    def get_absolute_url(self):
        return reverse('account_user_cart_detail')

    def __str__(self):
        return f'{self.user.username}\'s cart'


class UserCartBooksNumber(models.Model):
    cart = models.ForeignKey(UserCart, on_delete=models.CASCADE, related_name='books_numbers')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='carts_numbers')
    number = models.PositiveIntegerField(default=1)

    def calculate_total_price(self):
        price = self.book.off if self.book.off else self.book.price
        total_price = price * self.number
        return total_price

    def __str__(self):
        return f'{self.cart.user.username}\'s cart number of {self.book.title}'

    def clean(self):
        if not self.book.is_published():
            raise ValidationError('Book is not published!')

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.clean()
        if UserCartBooksNumber.objects.filter(pk=self.pk).exists():
            self.old_number = UserCartBooksNumber.objects.get(pk=self.pk).number

        return super().save(
            force_insert, force_update, using, update_fields
        )


class UserWish(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='wish_list')
    books = models.ManyToManyField(Book, related_name='in_wishlists', blank=True)

    def __str__(self):
        return f'{self.user.username}\'s wishlist'

    def get_absolute_url(self):
        return reverse('account_user_wishlist_detail')


@receiver(post_save, sender=get_user_model())
def create_user_cart_wish(instance, created, **kwargs):
    if created or not UserCart.objects.filter(user=instance).exists():
        UserCart.objects.create(user=instance)

    if created or not UserWish.objects.filter(user=instance).exists():
        UserWish.objects.create(user=instance)


@receiver(m2m_changed, sender=UserCart.books.through)
def update_user_cart_books_number(instance, action, pk_set, **kwargs):
    user_cart = UserCart.objects.get(pk=instance.pk)
    if action != 'pre_clear' and action != 'post_clear':
        pk_list = list(pk_set)

    if action == 'post_add':
        for pk in pk_list:
            book = Book.objects.get(pk=pk)
            UserCartBooksNumber.objects.create(
                cart=user_cart,
                book=book
            )

    if action == 'post_remove':
        for pk in pk_list:
            book = Book.objects.get(pk=pk)
            book.carts_numbers.get(cart=user_cart).delete()

    if action == 'post_clear':
        user_cart.books_numbers.all().delete()


@receiver(post_save, sender=UserCartBooksNumber)
def update_user_cart_books_number_number(instance, created, **kwargs):
    if not created:
        number = instance
        if number.number == 0:
            number.cart.books.remove(number.book)


@receiver(post_save, sender=UserCartBooksNumber)
def update_book_stock_by_cart_numbers(instance, created, **kwargs):
    number = instance.number
    book = instance.book
    if created:
        book.stock -= number
        book.save()
    elif getattr(instance, 'old_number') and instance.old_number != number:
        book.stock += instance.old_number
        book.stock -= number
    book.save()


@receiver(post_delete, sender=UserCartBooksNumber)
def rollback_book_stock_by_cart_numbers(instance, **kwargs):
    book = instance.book
    book.stock += instance.number
    book.save()
