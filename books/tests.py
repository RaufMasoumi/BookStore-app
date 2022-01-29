from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse, resolve
from decimal import Decimal
from .models import Book, Category, Review, ReviewReply
from . import views
# Create your tests here.


class BookTests(TestCase):

    def setUp(self):
        self.book = Book.objects.create(
            title='A new book',
            author='Rauf',
            price='30.00'
        )

        self.special_status_permission = Permission.objects.get(codename='special_status')
        self.add_book_permission = Permission.objects.get(codename='add_book')
        self.change_book_permission = Permission.objects.get(codename='change_book')
        self.delete_book_permission = Permission.objects.get(codename='delete_book')

        self.user = get_user_model().objects.create_user(
            username='testuser',
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
        self.client.logout()

    def test_book_list_view_for_logged_out_user(self):
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('account_login')}?next=/books/")
        response = self.client.get(f"{reverse('account_login')}?next=/books/")
        self.assertContains(response, 'Log In')

    def test_book_detail_view_with_permissions(self):
        self.client.force_login(self.user)
        self.user.user_permissions.add(self.special_status_permission)
        response = self.client.get(self.book.get_absolute_url())
        no_response = self.client.get('/books/12345/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, 'A new book')
        self.assertContains(response, 'A test review')
        self.assertNotContains(response, 'hi there i shooudlffsdf')
        self.assertTemplateUsed(response, 'books/book_detail.html')
        self.client.logout()

    def test_book_update_view_with_permissions(self):
        self.client.force_login(self.user)
        self.user.user_permissions.add(self.change_book_permission)
        self.user.user_permissions.add(self.special_status_permission)
        path = reverse('book_update', kwargs={'pk': self.book.pk})
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Update Book')
        self.assertTemplateUsed(get_response, 'books/book_update.html')
        data = {'author': 'RaufMasoumi', 'title': 'A new book(updated)', 'price': '1'}
        post_response = self.client.post(path, data)
        self.assertEqual(post_response.status_code, 302)
        self.book.refresh_from_db()
        self.assertEqual(self.book.author, 'RaufMasoumi')
        self.assertEqual(self.book.title, 'A new book(updated)')
        self.assertEqual(self.book.price, Decimal('1'))
        self.assertRedirects(post_response, self.book.get_absolute_url())
        self.client.logout()

    def test_book_create_view_with_permissions(self):
        self.client.force_login(self.user)
        self.user.user_permissions.add(self.add_book_permission)
        self.book.delete()
        path = reverse('book_create')
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Create Book')
        self.assertNotContains(get_response, 'Update_book')
        self.assertTemplateUsed(get_response, 'books/book_create.html')
        data = {'author': 'Rauf', 'title': 'A new book', 'price': '30.00'}
        post_response = self.client.post(path, data)
        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(Book.objects.count(), 1)
        book = Book.objects.all()[0]
        self.assertEqual(book.title, 'A new book')
        self.assertEqual(book.author, 'Rauf')
        self.assertEqual(book.price, Decimal('30.00'))
        self.client.logout()

    def test_book_delete_view_with_permissions(self):
        self.client.force_login(self.user)
        self.user.user_permissions.add(self.delete_book_permission)
        path = reverse('book_delete', kwargs={'pk': self.book.pk})
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Delete Book')
        self.assertNotContains(get_response, 'Update Book')
        self.assertTemplateUsed(get_response, 'books/book_delete.html')
        post_response = self.client.delete(path)
        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(Book.objects.count(), 0)
        self.assertRedirects(post_response, reverse('book_list'))


class CategoryTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.create_cat_permission = Permission.objects.get(codename='add_category')
        self.update_cat_permission = Permission.objects.get(codename='change_category')
        self.delete_cat_permission = Permission.objects.get(codename='delete_category')

        self.category = Category.objects.create(
            title='A test Category',
            position=1
        )

        self.book = Book.objects.create(
            title='A test book',
            author='Rauf',
            price='30.00',
        )

        self.book.category.add(self.category)
        self.client.force_login(self.user)

    def test_category_listing(self):
        self.assertEqual(self.category.title, 'A test Category')
        self.assertEqual(self.category.position, 1)

    def test_category_list_view(self):
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Categories List')
        self.assertContains(response, self.category.title)
        self.assertNotContains(response, 'Category Update')
        self.assertTemplateUsed(response, 'books/category/category_list.html')

    def test_category_detail_view(self):
        response = self.client.get(self.category.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.category.title)
        self.assertContains(response, self.book.title)
        self.assertNotContains(response, 'Category Update')
        self.assertTemplateUsed(response, 'books/category/category_detail.html')

    def test_category_create_view_with_permissions(self):
        path = reverse('category_create')
        self.user.user_permissions.add(self.create_cat_permission)
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Create Category')
        self.assertNotContains(get_response, 'Update Category')
        self.assertTemplateUsed(get_response, 'books/category/category_create.html')
        data = {'title': 'A new Category', 'position': 2}
        post_response = self.client.post(path, data)
        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(Category.objects.count(), 2)
        new_category = Category.objects.all()[1]
        self.assertEqual(new_category.title, 'A new Category')
        self.assertRedirects(post_response, reverse('category_list'))

    def test_category_update_view_with_permissions(self):
        path = reverse('category_update', kwargs={'pk': self.category.pk})
        self.user.user_permissions.add(self.update_cat_permission)
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Update Category')
        self.assertNotContains(get_response, 'Create Category')
        self.assertTemplateUsed(get_response, 'books/category/category_update.html')
        data = {'title': 'A test Category(updated)', 'position': 2}
        post_response = self.client.post(path, data)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, reverse('category_list'))
        self.category.refresh_from_db()
        self.assertEqual(self.category.title, 'A test Category(updated)')
        self.assertEqual(self.category.position, 2)

    def test_category_delete_view_with_permissions(self):
        path = reverse('category_delete', kwargs={'pk': self.category.pk})
        self.user.user_permissions.add(self.delete_cat_permission)
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Delete Category')
        self.assertNotContains(get_response, 'Update Category')
        self.assertTemplateUsed(get_response, 'books/category/category_delete.html')
        post_response = self.client.delete(path)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, reverse('category_list'))
        self.assertEqual(Category.objects.count(), 0)


class ReviewTests(TestCase):

    def setUp(self):
        self.author = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.permission = Permission.objects.get(codename='special_status')

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

        self.client.force_login(self.author)
        self.author.user_permissions.add(self.permission)

    def test_review_listing(self):
        self.assertEqual(self.review.review, 'A test review')
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.all()[0].review, 'A test review')

    def test_review_create_view(self):
        path = reverse('review_create')
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Create Review')
        self.assertNotContains(get_response, 'Update Review')
        self.assertTemplateUsed(get_response, 'books/reviews/review_create.html')
        post_response = self.client.post(path, {'book': self.book.pk, 'review': 'A new review'})
        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(Review.objects.count(), 2)
        self.assertEqual(Review.objects.all()[0].review, 'A new review')
        self.assertRedirects(post_response, self.book.get_absolute_url())

    def test_review_update_view_for_review_author(self):
        path = reverse('review_update', kwargs={'pk': self.review.pk})
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Update Review')
        self.assertNotContains(get_response, 'hi there I should not by in template!!')
        self.assertTemplateUsed(get_response, 'books/reviews/review_update.html')
        post_response = self.client.post(path, {'review': 'A test review (updated)'})
        self.review.refresh_from_db()
        self.assertEqual(self.review.review, 'A test review (updated)')
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, self.book.get_absolute_url())

    def test_review_delete_view_for_review_author(self):
        path = reverse('review_delete', kwargs={'pk': self.review.pk})
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Delete Review')
        self.assertNotContains(get_response, 'Update Review')
        self.assertTemplateUsed(get_response, 'books/reviews/review_delete.html')
        post_response = self.client.delete(path)
        self.assertEqual(Review.objects.count(), 0)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, self.book.get_absolute_url())


class ReviewRepliesTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.book = Book.objects.create(
            title='A new Book',
            author='Rauf',
            price='10'
        )

        self.review = Review.objects.create(
            book=self.book,
            author=self.user,
            review='The new Review'
        )

        self.review_reply = ReviewReply.objects.create(
            review=self.review,
            author=self.user,
            reply='The new review Reply'
        )
        self.client.force_login(self.user)
        self.user.user_permissions.add(Permission.objects.get(codename='special_status'))

    def test_review_reply_listing(self):
        self.assertEqual(ReviewReply.objects.count(), 1)
        self.assertEqual(ReviewReply.objects.all()[0], self.review_reply)
        self.assertEqual(self.review_reply.author, self.user)
        self.assertEqual(self.review_reply.review, self.review)
        self.assertEqual(self.review_reply.reply, 'The new review Reply')

    def test_review_reply_create_view_for_logged_in_user(self):
        path = reverse('reply_create')
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Create Review Reply')
        self.assertNotContains(get_response, 'Update Review Reply')
        self.assertTemplateUsed(get_response, 'books/reviews/replies/review_reply_create.html')
        post_response = self.client.post(path, {'review': self.review.pk, 'reply': 'the second review Reply'})
        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(ReviewReply.objects.count(), 2)
        self.assertEqual(ReviewReply.objects.all()[1].reply, 'the second review Reply')
        self.assertRedirects(post_response, self.book.get_absolute_url())

    def test_review_reply_update_view_for_reply_author(self):
        path = reverse('reply_update', kwargs={'pk': self.review_reply.pk})
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Update Review Reply')
        self.assertNotContains(get_response, 'Create Review Reply')
        self.assertTemplateUsed(get_response, 'books/reviews/replies/review_reply_update.html')
        post_response = self.client.post(path, {'reply': 'The review Reply'})
        self.review_reply.refresh_from_db()
        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(ReviewReply.objects.all()[0].reply, 'The review Reply')
        self.assertRedirects(post_response, self.book.get_absolute_url())

    def test_review_reply_delete_view_for_reply_author(self):
        path = reverse('reply_delete', kwargs={'pk': self.review_reply.pk})
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Delete Review Reply')
        self.assertNotContains(get_response, 'Create Review Reply')
        self.assertTemplateUsed(get_response, 'books/reviews/replies/review_reply_delete.html')
        post_response = self.client.delete(path)
        self.assertEqual(ReviewReply.objects.count(), 0)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, self.book.get_absolute_url())

