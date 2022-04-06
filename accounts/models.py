import django.conf
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from decimal import Decimal
import requests
import uuid

# Create your models here.


class CustomUser(AbstractUser):
    image = models.ImageField(upload_to='accounts/pictures/', blank=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=200, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('account_user_detail')


class UserAddress(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='addresses')
    address = models.CharField(max_length=500)

    class Meta:
        verbose_name_plural = 'user addresses'

    def __str__(self):
        return f'{self.user}\'s address'

    def get_absolute_url(self):
        return reverse("user_address_detail", kwargs={'pk': self.pk})
    
from books.models import Book


class UserCart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='cart')
    books = models.ManyToManyField(Book, related_name='in_carts', blank=True)

    def calculate_total_price(self):
        total_price = Decimal('00.00')
        for book in self.books.all():
            price = book.off if book.off else book.price
            total_price += price * UserCartBooksNumber.objects.get(cart=self, book=book).number
        return total_price

    def calculate_total_price_with_cost(self):
        total_price = self.calculate_total_price()
        return total_price + 3

    def get_absolute_url(self):
        return reverse('account_user_cart_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.user.username}\'s cart'


class UserWish(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='wish_list')
    books = models.ManyToManyField(Book, blank=True)

    def __str__(self):
        return f'{self.user.username}\'s wishlist'


class UserCartBooksNumber(models.Model):
    cart = models.ForeignKey(UserCart, on_delete=models.CASCADE, related_name='books_numbers')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='carts_numbers')
    number = models.PositiveIntegerField(default=1)

    def calculate_total_price(self):
        if self.book.off:
            price = self.book.off
        else:
            price = self.book.price
        total_price = price * self.number
        return total_price

    def __str__(self):
        return f'{self.cart.user.username}\'s cart number of {self.book.title}'


@receiver(post_save, sender=get_user_model())
def create_user_cart(instance, created, **kwargs):
    if created or not UserCart.objects.filter(user=instance).exists():
        UserCart.objects.create(user=instance)
        return print(f'the user cart created for {instance.username}!')


@receiver(post_save, sender=get_user_model())
def create_user_wish(instance, created, **kwargs):
    if created or not UserWish.objects.filter(user=instance).exists():
        UserWish.objects.create(user=instance)
        return print(f'the user wish list created for {instance.username}!')


@receiver(m2m_changed, sender=UserCart.books.through)
def update_user_cart_books_number(instance, action, pk_set, model, **kwargs):
    user_cart = UserCart.objects.get(pk=instance.pk)
    print(action)
    if action != 'pre_clear' and action != 'post_clear':
        pk_list = list(pk_set)

    if not model == Book:
        return 'Error when calculating the number of user cart books!!'

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
def update_user_cart_books_number_number(instance, created, **kwargs):
    if not created:
        number = UserCartBooksNumber.objects.get(id=instance.id)
        if number.number == 0:
            book = Book.objects.get(id=number.book.id)
            cart = UserCart.objects.get(id=number.cart.id)
            cart.books.remove(book)
            return print('the book deleted from cart cause its number is zero!')


@receiver(post_save, sender=SocialAccount)
def update_user_profile_image(instance, **kwargs):
    if instance.user.image:
        return
    else:
        response = requests.get(instance.extra_data['picture'])
        user = instance.user
        path = f'{django.conf.settings.MEDIA_ROOT}/accounts/pictures/{user.username}.png'
        image = open(path, 'wb')
        image.write(response.content)
        image.close()
        user.image = path.split('media')[1]
        user.save()
        
    return print('image sat for the user.')
