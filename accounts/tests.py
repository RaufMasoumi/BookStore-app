from django.test import TestCase
from django.contrib.auth import get_user_model
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
        self.assertEqual(user.password, 'testpass123')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_superuser_creation(self):
        superuser = get_user_model().objects.create_superuser(
            username='testsuperuser',
            email='testsuperuser@email.com',
            password='testsuperpass123',
        )
        self.assertEqual(get_user_model().objects.count(), 2)
        self.assertEqual(superuser.username, 'testsuperuser')
        self.assertEqual(superuser.email, 'testsuperuser@email.com')
        self.assertEqual(superuser.password, 'testsuperpass123')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
