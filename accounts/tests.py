from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import UserCart
from books.models import Book
from decimal import Decimal
import time
# Create your tests here.


class CustomUserTests(TestCase):

    def test_user_creation(self):
        user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123',
        )
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@email.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_superuser_creation(self):
        superuser = get_user_model().objects.create_superuser(
            username='testsuperuser',
            email='testsuperuser@email.com',
            password='testsuperpass123',
        )
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(superuser.username, 'testsuperuser')
        self.assertEqual(superuser.email, 'testsuperuser@email.com')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)


class UserCartTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123',
        )
        self.user_cart = UserCart.objects.get(user=self.user)

        # self.book = Book.objects.create(
        #     title='Test Book',
        #     author='Test User',
        #     price=Decimal('100.50')
        # )

    def test_user_cart_auto_creation(self):
        self.assertEqual(UserCart.objects.count(), 1)
        self.assertEqual(UserCart.objects.all()[0].user.username, self.user.username)
        self.assertEqual(UserCart.objects.all()[0], self.user_cart)

    # def test_user_cart_total_price_auto_editing(self):
    #     self.user_cart.cart.add(self.book)
    #     self.assertEqual(self.user_cart.total_price, Decimal('100.50'))
    #     self.user_cart.cart.remove(self.book)
    #     self.assertEqual(self.user_cart.total_price, Decimal('00.00'))



