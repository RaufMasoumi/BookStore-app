from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.http import HttpResponse
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
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='carts')
    cart = models.ManyToManyField(Book, related_name='in_carts', blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=00.00)

    def __str__(self):
        return f'{self.user.username}\'s cart'


@receiver(post_save, sender=get_user_model())
def create_user_cart(instance, created, **kwargs):
    if created:
        if UserCart.objects.filter(user=instance).exists():
            return HttpResponse('The singed up user already have a user cart!!', status=409)
        else:
            UserCart.objects.create(user=instance)
            return
    else:
        return HttpResponse('The user signing up was unsuccessful!!')


@receiver(m2m_changed, sender=UserCart.cart.through)
def update_user_cart_total_price(instance, action, pk_set, model, **kwargs):
    user_cart = UserCart.objects.get(pk=instance.pk)
    pk_list = list(pk_set)
    total_price = Decimal('00.00')
    for i in range(len(pk_list)):
        if model != Book:
            return HttpResponse('Error when calculating the total price of user cart!!', status=409)
        total_price += Book.objects.get(pk=pk_list[i]).price

    if action == 'post_add':
        user_cart.total_price += total_price
        user_cart.save()
        return print('post_adding done!', user_cart.total_price)

    elif action == 'post_remove':
        user_cart.total_price -= total_price
        if user_cart.total_price > 0:
            user_cart.save()

        else:
            user_cart.total_price = Decimal('00.00')
            user_cart.save()
        return print('post_removing done!', user_cart.total_price)

    elif action == 'post_clear':
        user_cart.total_price = Decimal('00.00')
        user_cart.save()
        return print('post_clearing done!', user_cart.total_price)

    return HttpResponse('Error when calculating the total price of user cart!!', status=409)



