from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from decimal import Decimal
from .models import Book, Category, Review, ReviewReply
from .views import BOOK_DISPLAY_FIELDS, ORDERING_DICT
# Create your tests here.


class BookTests(TestCase):

    def setUp(self):
        self.book = Book.objects.create(
            title='A new book',
            author='Rauf',
            price=100,
            summary='hello this book is so beautiful!'
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
            review='A test review',
            rating=10
        )

        self.category1 = Category.objects.create(
            title='Category1',
            position=1
        )

        self.category2 = Category.objects.create(
            parent=self.category1,
            title='Category2',
            position=2
        )

        self.category3 = Category.objects.create(
            parent=self.category2,
            title='Category3',
            position=3
        )

    def test_book_creation(self):
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(self.book.title, 'A new book')
        self.assertEqual(self.book.author, 'Rauf')
        self.assertEqual(self.book.price, Decimal('100'))

    def test_update_book_category_receiver(self):
        self.book.category.add(self.category3)
        self.book.save()
        self.book.refresh_from_db()
        new_category_queryset = self.book.category.all()
        should_contain_values = [self.category1, self.category2, self.category3]
        self.assertQuerysetEqual(new_category_queryset, should_contain_values, ordered=False)

    def test_update_book_rating_receiver(self):
        self.book.refresh_from_db()
        self.assertEqual(self.book.rating, 10)
        review2 = Review.objects.create(book=self.book, author=self.user, review='review', rating=5)
        self.book.refresh_from_db()
        rating_list = [self.review.rating, review2.rating]
        should_be_rating = round(sum(rating_list) / len(rating_list), 1)
        self.assertEqual(self.book.rating, should_be_rating)
        review2.delete()

    def test_book_detail_view(self):
        path = self.book.get_absolute_url()
        old_views = self.book.views
        response = self.client.get(path)
        self.book.refresh_from_db()
        new_views = self.book.views
        no_response = self.client.get('/books/12345/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        for field in BOOK_DISPLAY_FIELDS:
            readable_field = field.replace('_', ' ').capitalize()
            value = getattr(self.book, field, '')
            self.assertContains(response, readable_field)
            if value:
                self.assertContains(response, value)
        self.assertEqual(new_views, old_views + 1)
        self.assertContains(response, self.review.review)
        self.assertNotContains(response, 'Hello I should not be here')
        self.assertTemplateUsed(response, 'books/book_detail.html')

    def test_draft_book_detail_view_with_permissions(self):
        self.book.status = 'd'
        self.book.save()
        self.client.force_login(self.user)
        self.user.user_permissions.add(self.special_status_permission)
        response = self.client.get(self.book.get_absolute_url())
        no_response = self.client.get(f'/books/{self.book.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, f'{self.book.title} (draft)')
        for field in BOOK_DISPLAY_FIELDS:
            readable_field = field.replace('_', ' ').capitalize()
            value = getattr(self.book, field, '')
            self.assertContains(response, readable_field)
            if value:
                self.assertContains(response, value)
        self.assertContains(response, self.review.review)
        self.assertContains(response, 'Make Published')
        self.assertNotContains(response, 'Hello I should not be here.')
        self.assertTemplateUsed(response, 'books/draft_book_detail.html')
        self.book.status = 'p'
        self.book.save()
        self.client.logout()

    def test_book_create_view_with_permissions(self):
        self.client.force_login(self.user)
        self.user.user_permissions.add(self.add_book_permission)
        path = reverse('book_create')
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Create Book')
        self.assertNotContains(get_response, 'Hello I should not be here')
        self.assertTemplateUsed(get_response, 'books/book_create.html')
        post_data = {'author': 'Mohammad', 'title': 'A test book', 'price': '10'}
        post_response = self.client.post(path, post_data)
        self.assertEqual(post_response.status_code, 302)
        # ordering is time_to_sell so new-added book will be first book
        added_book = Book.objects.all()[0]
        self.assertRedirects(post_response, added_book.get_absolute_url())
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(added_book.title, post_data['title'])
        self.assertEqual(added_book.author, post_data['author'])
        self.assertEqual(added_book.price, Decimal(post_data['price']))
        added_book.delete()
        self.client.logout()

    def test_book_update_view_with_permissions(self):
        self.client.force_login(self.user)
        self.user.user_permissions.add(self.change_book_permission)
        path = reverse('book_update', kwargs={'pk': self.book.pk})
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Update Book')
        self.assertNotContains(get_response, 'Hello I should not be here.')
        self.assertTemplateUsed(get_response, 'books/book_update.html')
        post_data = {'author': 'RaufMasoumi', 'title': 'A new book(updated)', 'price': '1'}
        post_response = self.client.post(path, post_data)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, self.book.get_absolute_url())
        self.book.refresh_from_db()
        self.assertEqual(self.book.author, post_data['author'])
        self.assertEqual(self.book.title, post_data['title'])
        self.assertEqual(self.book.price, Decimal(post_data['price']))
        self.client.logout()

    def test_book_delete_view_with_permissions(self):
        self.client.force_login(self.user)
        self.user.user_permissions.add(self.delete_book_permission)
        path = reverse('book_delete', kwargs={'pk': self.book.pk})
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Delete Book')
        self.assertNotContains(get_response, 'Hello I should not be here.')
        self.assertTemplateUsed(get_response, 'books/book_delete.html')
        delete_response = self.client.delete(path)
        self.assertEqual(delete_response.status_code, 302)
        self.assertRedirects(delete_response, reverse('home'))
        self.assertEqual(Book.objects.count(), 0)
        self.client.logout()

    def test_book_make_published(self):
        self.client.force_login(self.user)
        self.user.user_permissions.add(self.change_book_permission)
        self.book.status = 'd'
        self.book.save()
        path = reverse('book_make_published')
        no_response = self.client.get(path)
        self.assertEqual(no_response.status_code, 405)
        data = {'book': self.book.pk, 'publish': 'on'}
        response = self.client.post(path, data)
        self.book.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.book.get_absolute_url())
        self.assertEqual(self.book.status, 'p')
        self.client.logout()


class CategoryTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.add_category_permission = Permission.objects.get(codename='add_category')
        self.update_category_permission = Permission.objects.get(codename='change_category')
        self.delete_category_permission = Permission.objects.get(codename='delete_category')
        self.category_list_permission = Permission.objects.get(codename='category_list')

        self.category = Category.objects.create(
            title='A test Category',
            position=1
        )

        self.book = Book.objects.create(
            title='A test book',
            author='Rauf',
            price=100.00,
        )

        self.book.category.add(self.category)

    def test_category_creation(self):
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(self.category.title, 'A test Category')
        self.assertEqual(self.category.position, 1)

    def test_category_list_view(self):
        self.client.force_login(self.user)
        self.user.user_permissions.add(self.category_list_permission)
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Categories List')
        self.assertContains(response, self.category.title)
        self.assertNotContains(response, 'Hey i should not be here.')
        self.assertTemplateUsed(response, 'books/category/category_list.html')
        self.client.logout()

    def test_category_books_list_view(self):
        path = self.category.get_absolute_url()
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.category.title)
        self.assertContains(response, self.book.title)
        self.assertNotContains(response, 'Hi there I should not be here.')
        self.assertTemplateUsed(response, 'books/category/category_books_list.html')

    def test_category_create_view_with_permissions(self):
        self.client.force_login(self.user)
        self.user.user_permissions.add(self.add_category_permission)
        path = reverse('category_create')
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Create Category')
        self.assertNotContains(get_response, 'Hello I should not be here.')
        self.assertTemplateUsed(get_response, 'books/category/category_create.html')
        post_data = {'title': 'A new Category', 'position': 2}
        post_response = self.client.post(path, post_data)
        self.assertEqual(post_response.status_code, 302)
        created_category = Category.objects.all()[1]
        self.assertRedirects(post_response, created_category.get_absolute_url())
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(created_category.title, post_data['title'])
        self.assertEqual(created_category.position, post_data['position'])
        created_category.delete()
        self.client.logout()

    def test_category_update_view_with_permissions(self):
        self.client.force_login(self.user)
        self.user.user_permissions.add(self.update_category_permission)
        path = reverse('category_update', kwargs={'pk': self.category.pk})
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Update Category')
        self.assertNotContains(get_response, 'Hi there I should not be here.')
        self.assertTemplateUsed(get_response, 'books/category/category_update.html')
        post_data = {'title': 'A test Category(updated)', 'position': 2}
        post_response = self.client.post(path, post_data)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, self.category.get_absolute_url())
        self.category.refresh_from_db()
        self.assertEqual(self.category.title, post_data['title'])
        self.assertEqual(self.category.position, post_data['position'])
        self.client.logout()

    def test_category_delete_view_with_permissions(self):
        self.client.force_login(self.user)
        self.user.user_permissions.add(self.delete_category_permission)
        self.user.user_permissions.add(self.category_list_permission)
        path = reverse('category_delete', kwargs={'pk': self.category.pk})
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Delete Category')
        self.assertNotContains(get_response, 'Hello I should not here!')
        self.assertTemplateUsed(get_response, 'books/category/category_delete.html')
        delete_response = self.client.delete(path)
        self.assertEqual(delete_response.status_code, 302)
        self.assertRedirects(delete_response, reverse('category_list'))
        self.assertEqual(Category.objects.count(), 0)
        self.client.logout()


class ReviewTests(TestCase):

    def setUp(self):
        self.author = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.book = Book.objects.create(
            title='A test book',
            author='Rauf',
            price=100
        )

        self.review = Review.objects.create(
            book=self.book,
            author=self.author,
            review='A test review'
        )

    def test_review_creation(self):
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(self.review.review, 'A test review')
        self.assertEqual(self.review.book, self.book)

    def test_update_review_name_and_email_by_user_receiver(self):
        self.assertEqual(self.review.name, self.author.username)
        self.assertEqual(self.review.email, self.author.email)

    def test_review_create_view(self):
        path = reverse('review_create')
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Create Review')
        self.assertNotContains(get_response, 'Hello I should not be here.')
        self.assertTemplateUsed(get_response, 'books/reviews/review_create.html')
        post_data = {'name': 'Mohammad', 'email': 'mohammad@email.com', 'book': self.book.pk, 'review': 'A new review'}
        post_response = self.client.post(path, post_data)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, self.book.get_absolute_url())
        self.assertEqual(Review.objects.count(), 2)
        created_review = Review.objects.all()[0]
        self.assertEqual(created_review.name, post_data['name'])
        self.assertEqual(created_review.email, post_data['email'])
        self.assertEqual(created_review.book.pk, post_data['book'])
        self.assertEqual(created_review.review, post_data['review'])
        created_review.delete()

    def test_review_update_view_for_review_author(self):
        self.client.force_login(self.author)
        path = reverse('review_update', kwargs={'pk': self.review.pk})
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Update Review')
        self.assertNotContains(get_response, 'Hi there I should not be here.')
        self.assertTemplateUsed(get_response, 'books/reviews/review_update.html')
        post_data = {'review': 'A test review (updated)'}
        post_response = self.client.post(path, post_data)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, self.book.get_absolute_url())
        self.review.refresh_from_db()
        self.assertEqual(self.review.review, post_data['review'])
        self.client.logout()

    def test_review_delete_view_for_review_author(self):
        self.client.force_login(self.author)
        path = reverse('review_delete', kwargs={'pk': self.review.pk})
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Delete Review')
        self.assertNotContains(get_response, 'Hello I should not be here.')
        self.assertTemplateUsed(get_response, 'books/reviews/review_delete.html')
        delete_response = self.client.delete(path)
        self.assertEqual(delete_response.status_code, 302)
        self.assertRedirects(delete_response, self.book.get_absolute_url())
        self.assertEqual(Review.objects.count(), 0)
        self.client.logout()


class ReviewReplyTests(TestCase):

    def setUp(self):
        self.author = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.book = Book.objects.create(
            title='A test Book',
            author='Rauf',
            price=100
        )

        self.review = Review.objects.create(
            book=self.book,
            author=self.author,
            review='A test Review'
        )

        self.review_reply = ReviewReply.objects.create(
            review=self.review,
            author=self.author,
            reply='A test review reply'
        )

    def test_review_reply_creation(self):
        self.assertEqual(ReviewReply.objects.count(), 1)
        self.assertEqual(self.review_reply.author, self.author)
        self.assertEqual(self.review_reply.review, self.review)
        self.assertEqual(self.review_reply.reply, 'A test review reply')

    def test_update_review_reply_name_and_email_by_user(self):
        self.assertEqual(self.review_reply.name, self.author.username)
        self.assertEqual(self.review_reply.email, self.author.email)

    def test_review_reply_create_view(self):
        path = reverse('reply_create')
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Create Review Reply')
        self.assertNotContains(get_response, 'Hi there I should not be here.')
        self.assertTemplateUsed(get_response, 'books/reviews/replies/review_reply_create.html')
        post_data = {'name': 'Mohammad', 'email': 'Mohammad@email.com', 'review': self.review.pk,
                     'reply': 'A new review reply'}
        post_response = self.client.post(path, post_data)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, self.book.get_absolute_url())
        self.assertEqual(ReviewReply.objects.count(), 2)
        created_reply = ReviewReply.objects.all()[0]
        self.assertEqual(created_reply.name, post_data['name'])
        self.assertEqual(created_reply.email, post_data['email'])
        self.assertEqual(created_reply.review.pk, post_data['review'])
        self.assertEqual(created_reply.reply, post_data['reply'])
        created_reply.delete()

    def test_review_reply_update_view_for_reply_author(self):
        self.client.force_login(self.author)
        path = reverse('reply_update', kwargs={'pk': self.review_reply.pk})
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Update Review Reply')
        self.assertNotContains(get_response, 'Hello I should not be here.')
        self.assertTemplateUsed(get_response, 'books/reviews/replies/review_reply_update.html')
        post_data = {'reply': 'A test review reply (updated)'}
        post_response = self.client.post(path, post_data)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, self.book.get_absolute_url())
        self.review_reply.refresh_from_db()
        self.assertEqual(self.review_reply.reply, post_data['reply'])
        self.client.logout()

    def test_review_reply_delete_view_for_reply_author(self):
        self.client.force_login(self.author)
        path = reverse('reply_delete', kwargs={'pk': self.review_reply.pk})
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Delete Review Reply')
        self.assertNotContains(get_response, 'Hey I should not be here.')
        self.assertTemplateUsed(get_response, 'books/reviews/replies/review_reply_delete.html')
        delete_response = self.client.delete(path)
        self.assertEqual(delete_response.status_code, 302)
        self.assertRedirects(delete_response, self.book.get_absolute_url())
        self.assertEqual(ReviewReply.objects.count(), 0)
        self.client.logout()

    def test_update_votes_view(self):
        path = reverse('votes_update')
        no_response = self.client.get(path)
        self.assertEqual(no_response.status_code, 405)
        positive_review_data = {'review': self.review.pk, 'positive': True}
        positive_review_response = self.client.post(path, positive_review_data)
        self.assertEqual(positive_review_response.status_code, 302)
        self.assertRedirects(positive_review_response, self.review.get_absolute_url())
        old_review_votes = self.review.votes
        self.review.refresh_from_db()
        new_review_votes = self.review.votes
        self.assertEqual(new_review_votes, old_review_votes + 1)
        negative_review_reply_data = {'reply': self.review_reply.pk}
        negative_review_reply_response = self.client.post(path, negative_review_reply_data)
        self.assertEqual(negative_review_reply_response.status_code, 302)
        self.assertRedirects(negative_review_reply_response, self.review_reply.get_absolute_url())
        old_review_reply_votes = self.review_reply.votes
        self.review_reply.refresh_from_db()
        new_review_reply_votes = self.review_reply.votes
        self.assertEqual(new_review_reply_votes, old_review_reply_votes - 1)


class SearchResultsViewTests(TestCase):

    def setUp(self):

        self.book1 = Book.objects.create(
            title='First book',
            author='RaufMasoumi',
            price=100
        )

        self.book2 = Book.objects.create(
            title='Second book',
            author='RaufMasoumi',
            price=100
        )

        self.path = reverse('search_results')

    def test_search_results_status_code(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)

    def test_search_results_template(self):
        response = self.client.get(self.path)
        self.assertTemplateUsed(response, 'books/search_results.html')
        comparing_response = self.client.get(self.path, {'come_from_comparing': True})
        self.assertTemplateUsed(comparing_response, 'books/book_add_to_comparing_list.html')

    def test_search_results_searching(self):
        query1 = 'first'
        response1 = self.client.get(self.path, {'query': query1})
        search_book_list1 = response1.context['search_book_list']
        self.assertIn(self.book1, search_book_list1)
        self.assertNotIn(self.book2, search_book_list1)
        query2 = 'second'
        response2 = self.client.get(self.path, {'query': query2})
        search_book_list2 = response2.context['search_book_list']
        self.assertIn(self.book2, search_book_list2)
        self.assertNotIn(self.book1, search_book_list2)
        query3 = 'book'
        response3 = self.client.get(self.path, {'query': query3})
        search_book_list3 = response3.context['search_book_list']
        self.assertIn(self.book1, search_book_list3)
        self.assertIn(self.book2, search_book_list3)
        query4 = 'raufmasoumi'
        response4 = self.client.get(self.path, {'query': query4})
        search_book_list4 = response4.context['search_book_list']
        self.assertIn(self.book1, search_book_list4)
        self.assertIn(self.book2, search_book_list4)
        query5 = 'Hello I should not be in search results.'
        response5 = self.client.get(self.path, {'query': query5})
        search_book_list5 = response5.context['search_book_list']
        self.assertNotIn(self.book1, search_book_list5)
        self.assertNotIn(self.book2, search_book_list5)
        response6 = self.client.get(self.path)
        search_book_list6 = response6.context['search_book_list']
        self.assertIn(self.book1, search_book_list6)
        self.assertIn(self.book2, search_book_list6)

    def test_search_results_getting_books_from_comparing(self):
        data = {'come_from_comparing': True, 'book-1': self.book1.pk}
        response = self.client.get(self.path, data)
        books_comparing_get_dict = response.context['books_comparing_get_dict']
        new_book_comparing_get_pattern = response.context['new_book_comparing_get_pattern']
        self.assertEqual(books_comparing_get_dict['book-1'], self.book1.pk)
        self.assertEqual(new_book_comparing_get_pattern, 'book-2')


class BookComparingViewTests(TestCase):

    def setUp(self):
        self.book1 = Book.objects.create(
            title='First book',
            author='RaufMasoumi',
            price=100
        )

        self.book2 = Book.objects.create(
            title='Second book',
            author='Mohammad Rauf Masoumi',
            price=10
        )

        self.book3 = Book.objects.create(
            title='Third book',
            author='Lewis Capaldi',
            price=1
        )

        self.path = reverse('book_comparing')

    def test_book_comparing_status_code(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        no_response = self.client.post(self.path)
        self.assertEqual(no_response.status_code, 405)

    def test_book_comparing_template(self):
        response = self.client.get(self.path)
        self.assertTemplateUsed(response, 'books/book_comparing.html')

    def test_book_comparing_with_empty_request(self):
        response = self.client.get(self.path)
        comparing_dict = response.context['comparing_dict']
        self.assertContains(response, 'There is no books to compare!')
        for attr_list in comparing_dict.values():
            self.assertEqual(len(attr_list), 0)

    def test_book_comparing_getting_books(self):
        data = {'book-1': self.book1.pk, 'book-2': self.book2.pk, 'book-3': self.book3.pk}
        response = self.client.get(self.path, data)
        books_list = response.context['books']
        self.assertEqual(len(books_list), 3)
        self.assertEqual(books_list[0], self.book1)
        self.assertEqual(books_list[1], self.book2)
        self.assertEqual(books_list[2], self.book3)

    def test_book_comparing_field_ordering(self):
        data = {'book-1': self.book1.pk, 'book-2': self.book2.pk, 'book-3': self.book3.pk}
        response = self.client.get(self.path, data)
        comparing_dict = response.context['comparing_dict']
        for field in BOOK_DISPLAY_FIELDS:
            human_readable_field = field.replace('_', ' ').capitalize()
            field_value_list = comparing_dict[human_readable_field]
            self.assertEqual(field_value_list[0], getattr(self.book1, field, ''))
            self.assertEqual(field_value_list[1], getattr(self.book2, field, ''))
            self.assertEqual(field_value_list[2], getattr(self.book3, field, ''))

    def test_book_comparing_containing(self):
        data = {'book-1': self.book1.pk, 'book-2': self.book2.pk, 'book-3': self.book3.pk}
        response = self.client.get(self.path, data)
        for field in BOOK_DISPLAY_FIELDS:
            human_readable_field = field.replace('_', ' ').capitalize()
            self.assertContains(response, human_readable_field)
            book1_attr = getattr(self.book1, field, '')
            if book1_attr:
                self.assertContains(response, book1_attr)
            book2_attr = getattr(self.book2, field, '')
            if book2_attr:
                self.assertContains(response, book2_attr)
            book3_attr = getattr(self.book3, field, '')
            if book3_attr:
                self.assertContains(response, book3_attr)

    def test_book_comparing_deleting(self):
        data = {'book-1': self.book1.pk, 'book-2': self.book2.pk, 'book-3': self.book3.pk,
                'delete_book': self.book2.pk}
        response = self.client.get(self.path, data)
        books_list = response.context['books']
        self.assertEqual(len(books_list), 2)
        self.assertEqual(books_list[0], self.book1)
        self.assertEqual(books_list[1], self.book3)

    def test_book_comparing_books_get_dict(self):
        data = {'book-1': self.book1.pk, 'book-2': self.book2.pk, 'book-3': self.book3.pk}
        response = self.client.get(self.path, data)
        books_get_dict = response.context['books_get_dict']
        self.assertDictEqual(books_get_dict, data)


class BookFilteringLimitingShowingTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.special_status_permission = Permission.objects.get(codename='special_status')

        self.category = Category.objects.create(
            title='A test Category',
            position=1
        )

        self.book1 = Book.objects.create(
            title='test book1',
            author='RaufMasoumi',
            price=100,
        )
        self.book1.category.add(self.category)

        self.book2 = Book.objects.create(
            title='test book2',
            author='RaufMasoumi',
            price=10
        )
        self.book2.category.add(self.category)

        self.book3 = Book.objects.create(
            title='test book3',
            author='RaufMasoumi',
            price=1
        )
        self.book3.category.add(self.category)

        self.path = reverse('category_books_list', kwargs={'pk': self.category.pk})

    def test_published_limit_without_permissions(self):
        self.client.force_login(self.user)
        self.book1.status = 'd'
        self.book1.save()
        self.book1.refresh_from_db()
        response = self.client.get(self.path)
        books = response.context['category_books']
        should_be_values = [book for book in [self.book1, self.book2, self.book3] if book.status == 'p']
        self.assertQuerysetEqual(books, should_be_values, ordered=False)
        self.client.logout()

    def test_published_limit_with_permissions(self):
        self.client.force_login(self.user)
        self.user.user_permissions.add(self.special_status_permission)
        response = self.client.get(self.path)
        books = response.context['category_books']
        should_be_values = [self.book1, self.book2, self.book3]
        self.assertQuerysetEqual(books, should_be_values, ordered=False)
        self.book1.status = 'p'
        self.book1.save()
        self.client.logout()

    def test_price_limit(self):
        data = {'filter': True, 'use_price': True, 'amount': '$101 - $9'}
        response = self.client.get(self.path, data)
        books = response.context['category_books']
        price_on_key = response.context['price_on_key']
        price_less = response.context['price_less_key']
        price_more = response.context['price_more_key']
        should_be_values = [self.book1, self.book2]
        self.assertTrue(price_on_key)
        self.assertEqual(price_less, 9)
        self.assertEqual(price_more, 101)
        self.assertQuerysetEqual(books, should_be_values, ordered=False)

    def test_available_limit_with_available_sending(self):
        data = {'filter': True, 'use_availability': True, 'available': True}
        response = self.client.get(self.path, data)
        books = response.context['category_books']
        available_on_key = response.context['available_on_key']
        availability_on_key = response.context['availability_on_key']
        should_be_values = [book for book in [self.book1, self.book2, self.book3] if book.stock > 0]
        self.assertTrue(availability_on_key)
        self.assertEqual(available_on_key, 'available')
        self.assertQuerysetEqual(books, should_be_values, ordered=False)

    def test_available_limit_with_unavailable_sending(self):
        data = {'filter': True, 'use_availability': True, 'unavailable': True}
        response = self.client.get(self.path, data)
        books = response.context['category_books']
        available_on_key = response.context['available_on_key']
        availability_on_key = response.context['availability_on_key']
        should_be_values = [book for book in [self.book1, self.book2, self.book3] if book.stock < 1]
        self.assertTrue(availability_on_key)
        self.assertEqual(available_on_key, 'unavailable')
        self.assertQuerysetEqual(books, should_be_values, ordered=False)

    def test_available_limit_with_both_sending(self):
        data = {'filter': True, 'use_availability': True, 'available': True, 'unavailable': True}
        response = self.client.get(self.path, data)
        books = response.context['category_books']
        available_on_key = response.context['available_on_key']
        availability_on_key = response.context['availability_on_key']
        should_be_values = [self.book1, self.book2, self.book3]
        self.assertTrue(availability_on_key)
        self.assertEqual(available_on_key, 'both')
        self.assertQuerysetEqual(books, should_be_values, ordered=False)

    def test_sort_books(self):
        data = {'showing': True, 'sort': '-price'}
        response = self.client.get(self.path, data)
        books = response.context['category_books']
        order_by = response.context['order_by']
        should_be_values = [self.book1, self.book2, self.book3]
        should_be_dict = {data['sort']: ORDERING_DICT.get(data['sort'])}
        self.assertIsInstance(order_by, dict)
        self.assertDictEqual(order_by, should_be_dict)
        self.assertQuerysetEqual(books, should_be_values)

    def test_paginate_books_with_correct_show(self):
        data = {'showing': True, 'show': 9}
        response = self.client.get(self.path, data)
        paginate_by = response.context['paginate_by']
        self.assertEqual(paginate_by, data['show'])

    def test_paginate_books_with_incorrect_show(self):
        data = {'showing': True, 'show': 123}
        response = self.client.get(self.path, data)
        paginate_by = response.context['paginate_by']
        self.assertEqual(paginate_by, 9)
