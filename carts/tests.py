from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from books.models import Book
from .models import UserCart, UserCartBooksNumber, UserWish
# Create your tests here.


class UserCartTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123',
        )

        self.cart = self.user.cart

        self.book = Book.objects.create(
            title='A test book',
            author='Rauf',
            price='100.50',
            stock=10,
        )

    def test_user_cart_create_receiver(self):
        self.assertEqual(UserCart.objects.count(), 1)
        self.assertEqual(UserCart.objects.all()[0], self.cart)

    def test_user_cart_detail_view_for_test_passed_user(self):
        self.client.force_login(self.user)
        self.cart.books.add(self.book)
        path = reverse('account_user_cart_detail', kwargs={'pk': self.cart.pk})
        path_without_pk = reverse('account_user_cart_detail')
        response = self.client.get(path)
        response_without_pk = self.client.get(path_without_pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_without_pk.status_code, 200)
        self.assertContains(response, 'Shopping cart')
        self.assertContains(response_without_pk, 'Shopping cart')
        self.assertContains(response, self.book.title)
        self.assertNotContains(response, 'Log In')
        self.assertTemplateUsed(response, 'carts/user_cart_detail.html')
        self.cart.books.remove(self.book)
        self.client.logout()

    def test_user_cart_update_view_for_test_passed_user(self):
        self.client.force_login(self.user)
        path = reverse('account_user_cart_update')
        user_cart_path = self.cart.get_absolute_url()
        no_response = self.client.get(path)
        self.assertEqual(no_response.status_code, 405)
        book_add_response = self.client.post(path, {'book_pk': self.book.pk})
        self.assertEqual(book_add_response.status_code, 302)
        self.assertRedirects(book_add_response, user_cart_path)
        self.assertEqual(self.cart.books.count(), 1)
        added_book = self.cart.books.all()[0]
        self.assertEqual(added_book, self.book)
        old_stock = self.book.stock
        self.book.refresh_from_db()
        new_stock = self.book.stock
        self.assertEqual(old_stock - 1, new_stock)
        book_number = UserCartBooksNumber.objects.get(cart=self.cart, book=self.book)
        self.assertEqual(book_number.number, 1)
        old_stock = self.book.stock
        old_number = book_number.number
        delete_response = self.client.post(path, {'delete_book_pk': self.book.pk})
        self.assertEqual(delete_response.status_code, 302)
        self.assertRedirects(delete_response, user_cart_path)
        self.book.refresh_from_db()
        self.cart.refresh_from_db()
        new_stock = self.book.stock
        self.assertEqual(new_stock, old_stock + old_number)
        self.assertEqual(self.cart.books.count(), 0)
        quantity = 5
        old_stock = self.book.stock
        quantity_book_data = {'quantity': quantity, 'book_pk': self.book.pk}
        quantity_book_response = self.client.post(path, quantity_book_data)
        self.assertEqual(quantity_book_response.status_code, 302)
        self.assertRedirects(quantity_book_response, user_cart_path)
        self.assertEqual(self.cart.books.count(), 1)
        added_book = self.cart.books.all()[0]
        self.assertEqual(added_book, self.book)
        self.book.refresh_from_db()
        book_number = UserCartBooksNumber.objects.get(cart=self.cart, book=added_book)
        new_stock = self.book.stock
        self.assertEqual(new_stock, old_stock - quantity)
        self.assertEqual(book_number.number, quantity)
        quantity = 10
        quantity_number_data = {'quantity': quantity, 'number_pk': book_number.pk}
        quantity_number_response = self.client.post(path, quantity_number_data)
        self.assertEqual(quantity_number_response.status_code, 302)
        self.assertRedirects(quantity_number_response, user_cart_path)
        old_stock = self.book.stock + book_number.number
        self.book.refresh_from_db()
        book_number.refresh_from_db()
        new_stock = self.book.stock
        self.assertEqual(new_stock, old_stock - quantity)
        self.assertEqual(book_number.number, quantity)
        self.client.logout()


class UserCartBooksNumberTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123',
        )

        self.cart = self.user.cart

        self.book = Book.objects.create(
            title='A test book',
            author='Rauf',
            price='100.50',
            stock=10,
        )

    def test_update_user_cart_books_number_receiver(self):
        self.cart.books.add(self.book)
        self.assertEqual(UserCartBooksNumber.objects.count(), 1)
        created_number = UserCartBooksNumber.objects.all()[0]
        self.assertEqual(created_number.cart, self.cart)
        self.assertEqual(created_number.book, self.book)
        self.cart.books.remove(self.book)
        self.assertEqual(UserCartBooksNumber.objects.count(), 0)
        self.cart.books.add(self.book)
        self.cart.books.clear()
        self.assertEqual(UserCartBooksNumber.objects.count(), 0)

    def test_update_user_cart_books_number_number_receiver(self):
        self.cart.books.add(self.book)
        created_number = UserCartBooksNumber.objects.all()[0]
        created_number.number = 0
        created_number.save()
        self.assertEqual(self.cart.books.count(), 0)
        self.assertEqual(UserCartBooksNumber.objects.count(), 0)


class UserWishTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
        )

        self.wish = self.user.wish_list

        self.book = Book.objects.create(
            title='test_book',
            author='test_author',
            price='100',
            stock=10
        )

    def test_user_wish_create_receiver(self):
        self.assertEqual(UserWish.objects.count(), 1)
        self.assertEqual(UserWish.objects.all()[0], self.wish)

    def test_user_wish_detail_view_for_test_passed_user(self):
        self.client.force_login(self.user)
        self.wish.books.add(self.book)
        path = reverse('account_user_wishlist_detail', kwargs={'pk': self.wish.pk})
        path_without_pk = reverse('account_user_wishlist_detail')
        response = self.client.get(path)
        response_without_pk = self.client.get(path_without_pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_without_pk.status_code, 200)
        self.assertContains(response, 'My Wish List')
        self.assertContains(response_without_pk, 'My Wish List')
        self.assertContains(response, self.book.title)
        self.assertNotContains(response, 'My Cart')
        self.assertTemplateUsed(response, 'carts/user_wishlist_detail.html')
        self.wish.books.remove(self.book)
        self.client.logout()

    def test_user_wish_update_view_for_test_passed_user(self):
        self.client.force_login(self.user)
        path = reverse('account_user_wishlist_update')
        user_wish_path = self.wish.get_absolute_url()
        no_response = self.client.get(path)
        self.assertEqual(no_response.status_code, 405)
        add_data = {'book_id': self.book.pk, 'add': True}
        book_add_response = self.client.post(path, add_data)
        self.assertEqual(book_add_response.status_code, 302)
        self.assertRedirects(book_add_response, user_wish_path)
        self.wish.refresh_from_db()
        self.assertEqual(self.wish.books.count(), 1)
        self.assertEqual(self.wish.books.all()[0], self.book)
        delete_data = {'book_id': self.book.pk, 'delete': True}
        book_delete_response = self.client.post(path, delete_data)
        self.assertEqual(book_delete_response.status_code, 302)
        self.assertRedirects(book_delete_response, user_wish_path)
        self.wish.refresh_from_db()
        self.assertEqual(self.wish.books.count(), 0)
        self.client.logout()
