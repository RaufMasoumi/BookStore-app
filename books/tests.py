from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from .models import Book, Review
# Create your tests here.


class BookTests(TestCase):

    def setUp(self):
        self.book = Book.objects.create(
            title='A new book',
            author='Rauf',
            price='30.00'
        )

        self.permission = Permission.objects.get(codename='special_status')

        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123'
        )

        self.review = Review.objects.create(
            book=self.book,
            author=self.user,
            review='A test review'
        )

    def test_book_listing(self):
        self.assertEqual(self.book.title, 'A new book')
        self.assertEqual(self.book.author, 'Rauf')
        self.assertEqual(self.book.price, '30.00')

    def test_book_list_view_for_logged_in_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Books List')
        self.assertNotContains(response, 'hi there i shooudlffsdf')
        self.assertTemplateUsed(response, 'books/book_list.html')

    def test_book_list_view_for_logged_out_user(self):
        self.client.logout()
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 302)

    def test_book_detail_view_with_permissions(self):
        self.client.force_login(self.user)
        self.user.user_permissions.add(self.permission)
        response = self.client.get(self.book.get_absolute_url())
        no_response = self.client.get('/books/12345/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, 'A new book')
        self.assertContains(response, 'A test review')
        self.assertNotContains(response, 'hi there i shooudlffsdf')
        self.assertTemplateUsed(response, 'books/book_detail.html')


class ReviewTests(TestCase):

    def setUp(self):
        self.author = get_user_model().objects.create_user(
            email='testuser@email.com',
            username='testuser',
            password='testpass123'
        )

        self.book = Book.objects.create(
            title='A new book',
            author='Rauf',
            price='30.00'
        )

        self.review = Review.objects.create(
            book=self.book,
            author=self.author,
            review='A test review'
        )

    def test_review_listing(self):
        self.assertEqual(self.review.review, 'A test review')
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.all()[0].review, 'A test review')

