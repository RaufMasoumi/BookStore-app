from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from books.models import Book
from .models import Review, ReviewReply
# Create your tests here.


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
        self.assertTemplateUsed(get_response, 'reviews/review_create.html')
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
        self.assertTemplateUsed(get_response, 'reviews/review_update.html')
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
        self.assertTemplateUsed(get_response, 'reviews/review_delete.html')
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
        self.assertTemplateUsed(get_response, 'reviews/replies/review_reply_create.html')
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
        self.assertTemplateUsed(get_response, 'reviews/replies/review_reply_update.html')
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
        self.assertTemplateUsed(get_response, 'reviews/replies/review_reply_delete.html')
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
