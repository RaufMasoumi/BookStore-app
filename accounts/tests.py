from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import UserCart, UserCartBooksNumber
from books.models import Book
# Create your tests here.


class CustomUserTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123',
        )

    def test_user_creation(self):
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'testuser@email.com')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_superuser)
        self.assertFalse(self.user.is_staff)

    def test_superuser_creation(self):
        superuser = get_user_model().objects.create_superuser(
            username='testsuperuser',
            email='testsuperuser@email.com',
            password='testsuperpass123',
        )
        self.assertEqual(get_user_model().objects.count(), 2)
        self.assertEqual(superuser.username, 'testsuperuser')
        self.assertEqual(superuser.email, 'testsuperuser@email.com')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_user_profile_update_view_for_test_passed_user(self):
        self.client.force_login(self.user)
        path = reverse('account_user_update', kwargs={'pk': self.user.pk})
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Update Profile')
        self.assertTemplateUsed(get_response, 'account/user_update.html')
        post_response = self.client.post(path, data={'first_name': 'user'})
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, reverse('home'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'user')


class UserCartTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123',
        )

        self.user_cart = UserCart.objects.get(user=self.user)

        self.book = Book.objects.create(
            title='A test book',
            author='Rauf',
            price='100.50',
            stock=10,
        )

    def test_user_cart_auto_creation_and_listing(self):
        self.assertEqual(UserCart.objects.count(), 1)
        self.user_cart = UserCart.objects.get(user=self.user)
        self.assertEqual(UserCart.objects.all()[0], self.user_cart)
        self.assertEqual(UserCart.objects.all()[0].user, self.user)

    def test_user_cart_detail_view_for_test_passed_user(self):
        self.client.force_login(self.user)
        self.user_cart.cart.add(self.book)
        response = self.client.get(reverse('account_user_cart_detail', kwargs={'pk': self.user_cart.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User Cart')
        self.assertContains(response, self.book.title)
        self.assertNotContains(response, 'Log In')
        self.assertTemplateUsed(response, 'account/user_cart_detail.html')
        self.user_cart.cart.remove(self.book)

    def test_user_cart_books_number_updating(self):
        self.user_cart.cart.add(self.book)
        self.assertEqual(UserCartBooksNumber.objects.count(), 1)
        number = UserCartBooksNumber.objects.all()[0]
        self.assertEqual(number.book, self.book)
        self.assertEqual(number.cart, self.user_cart)
        self.user_cart.cart.remove(self.book)
        self.assertFalse(UserCartBooksNumber.objects.filter(id=number.id).exists())
        new_book = Book.objects.create(title='The hello', author='hello', price=1)
        self.user_cart.cart.add(new_book)
        self.user_cart.cart.add(self.book)
        self.user_cart.cart.clear()
        self.assertEqual(UserCartBooksNumber.objects.count(), 0)

    def test_user_cart_books_number_number_updating(self):
        self.user_cart.cart.add(self.book)
        number = UserCartBooksNumber.objects.get(cart=self.user_cart, book=self.book)
        number.number = 0
        number.save()
        self.assertEqual(UserCartBooksNumber.objects.count(), 0)

    def test_user_cart_update_view_for_logged_in_and_passed_test_user(self):
        self.client.force_login(self.user)
        path = reverse('account_user_cart_update')
        user_cart_path = reverse('account_user_cart_detail', kwargs={'pk': self.user_cart.pk})
        no_response = self.client.get(path)
        self.assertEqual(no_response.status_code, 405)
        book_add_response = self.client.post(path, {'book_add': self.book.id})
        self.assertEqual(book_add_response.status_code, 302)
        self.assertRedirects(book_add_response, user_cart_path)
        self.assertEqual(self.user_cart.cart.count(), 1)
        added_book = self.user_cart.cart.all()[0]
        self.assertEqual(added_book, self.book)
        book_number = UserCartBooksNumber.objects.get(cart=self.user_cart, book=added_book)
        old_number = book_number.number
        old_stock = book_number.book.stock
        add_response = self.client.post(path, {'add': book_number.id})
        self.assertEqual(add_response.status_code, 302)
        self.assertRedirects(add_response, user_cart_path)
        book_number.refresh_from_db()
        self.assertEqual(book_number.number, old_number + 1)
        self.assertEqual(book_number.book.stock, old_stock - 1)
        old_number = book_number.number
        old_stock = book_number.book.stock
        reduce_response = self.client.post(path, {'reduce': book_number.id})
        self.assertEqual(reduce_response.status_code, 302)
        self.assertRedirects(reduce_response, user_cart_path)
        book_number.refresh_from_db()
        self.assertEqual(book_number.number, old_number - 1)
        self.assertEqual(book_number.book.stock, old_stock + 1)
        book = book_number.book
        old_stock = book_number.book.stock
        old_number = book_number.number
        delete_response = self.client.post(path, {'delete': book_number.id})
        self.assertEqual(delete_response.status_code, 302)
        self.assertRedirects(delete_response, user_cart_path)
        book.refresh_from_db()
        self.user_cart.refresh_from_db()
        self.assertEqual(book.stock, old_stock + old_number)
        self.assertEqual(self.user_cart.cart.count(), 0)
