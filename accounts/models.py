from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.http import HttpResponse
from django.urls import reverse
import uuid
from decimal import Decimal

# Create your models here.


class CustomUser(AbstractUser):
    image = models.ImageField(upload_to='accounts/', blank=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=300, blank=True, null=True)
    card_number = models.CharField(max_length=200, blank=True, null=True)
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=00.00)


from books.models import Book


class UserCart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='carts')
    cart = models.ManyToManyField(Book, related_name='in_carts', blank=True)

    def get_absolute_url(self):
        return reverse('account_usercart_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.user.username}\'s cart'


class UserCartBooksNumber(models.Model):
    cart = models.ForeignKey(UserCart, on_delete=models.CASCADE, related_name='books_numbers')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='carts_numbers')
    number = models.PositiveIntegerField(default=1, max_length=2)

    def __str__(self):
        return f'{self.cart.user.username}\'s cart{self.cart.pk} number of {self.book.title}'


@receiver(post_save, sender=get_user_model())
def create_user_cart(instance, created, **kwargs):
    if created:
        if UserCart.objects.filter(user=instance).exists():
            return HttpResponse('The singed up user already have a user cart!!', status=409)
        else:
            UserCart.objects.create(user=instance)
            return print('the usercart created for the new user!')
    else:
        return HttpResponse('The user signing up was unsuccessful!!')


@receiver(m2m_changed, sender=UserCart.cart.through)
def update_user_cart_books_number(instance, action, pk_set, model, **kwargs):
    user_cart = UserCart.objects.get(pk=instance.pk)
    pk_list = list(pk_set)

    if model != Book:
        return HttpResponse('Error when calculating the number of user cart books!!', status=409)

    if action == 'post_add':
        for i in range(len(pk_list)):
            book = Book.objects.get(pk=pk_list[i])
            UserCartBooksNumber.objects.create(
                cart=user_cart,
                book=book
            )
            print(f'the number for book with \"{book.title}\" title added.')
        return

    if action == 'post_remove':
        for i in range(len(pk_list)):
            book = Book.objects.get(pk=pk_list[i])
            if UserCartBooksNumber.objects.filter(cart=user_cart, book=book).exists():
                UserCartBooksNumber.objects.get(cart=user_cart, book=book).delete()
            print(f'the number for book with \"{book.title}\" title removed.')
        return

    if action == 'post_clear':
        if UserCartBooksNumber.objects.filter(cart=user_cart).exists():
            for number in UserCartBooksNumber.objects.filter(cart=user_cart):
                number.delete()
        return print(f'the numbers for books of user cart with {user_cart.pk} pk'
                     f' for {user_cart.user.username} cleared.')


@receiver(post_save, sender=UserCartBooksNumber)
def update_user_cart_books_number_number_and_stock(instance, created, **kwargs):
    if not created:
        number = UserCartBooksNumber.objects.get(id=instance.id)
        if number.number == 0:
            book = Book.objects.get(id=number.book.id)
            cart = UserCart.objects.get(id=number.cart.id)
            cart.cart.remove(book)
            return print('the book deleted from cart cause its number is zero!')

# @receiver(m2m_changed, sender=UserCart.cart.through)
# def update_user_cart_total_price(instance, action, pk_set, model, **kwargs):
#     user_cart = UserCart.objects.get(pk=instance.pk)
#     pk_list = list(pk_set)
#     total_price = Decimal('00.00')
#
#     if model != Book:
#         return HttpResponse('Error when calculating the total price of user cart!!', status=409)
#
#     for i in range(len(pk_list)):
#         price = Book.objects.get(pk=pk_list[i]).price
#         if UserCartBooksNumber.objects.filter(cart=user_cart, book__pk=pk_list[i]).exists():
#             number = UserCartBooksNumber.objects.get(cart=user_cart, book__pk=pk_list[i]).number
#             total_price += price * Decimal(number)
#         else:
#             number = 1
#             total_price += price * Decimal(number)
#
#     if action == 'post_add':
#         user_cart.total_price += total_price
#         user_cart.save()
#         return print('post_adding done!', user_cart.total_price)
#
#     elif action == 'post_remove':
#         user_cart.total_price -= total_price
#         if user_cart.total_price > 0:
#             user_cart.save()
#
#         else:
#             user_cart.total_price = Decimal('00.00')
#             user_cart.save()
#         return print('post_removing done!', user_cart.total_price)
#
#     elif action == 'post_clear':
#         user_cart.total_price = Decimal('00.00')
#         user_cart.save()
#         return print('post_clearing done!', user_cart.total_price)
#
#     return HttpResponse('Error when calculating the total price of user cart!!', status=409)
#
#
# @receiver(post_save, sender=UserCartBooksNumber)
# def update_user_cart_total_price_by_number(instance, created, update_fields, **kwargs):
#     if created:
#         return
#     cart = instance.cart
#     number = instance.number
#     price = instance.book.price
#     total_price = cart.total_price - price
#     total_price += price * number
#     cart.total_price = total_price
#     cart.save()
#     return print(f'total price updating by number done. total price:{total_price} | added price:{}')
