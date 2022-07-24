from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from books.models import Book
from .models import Category
# Create your tests here.


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
