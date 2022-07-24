from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import UserAddress
from .views import ACCOUNT_DISPLAY_FIELDS
# Create your tests here.


class CustomUserTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            phone_number='0901',
            card_number='1234',
            password='testpass123',
        )

    def test_user_creation(self):
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'testuser@email.com')
        self.assertEqual(self.user.phone_number, '0901')
        self.assertEqual(self.user.card_number, '1234')
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

    def test_user_profile_detail_view_for_test_passed_user(self):
        self.client.force_login(self.user)
        path = reverse('account_user_detail', kwargs={'pk': self.user.pk})
        path_without_pk = reverse('account_user_detail')
        get_response = self.client.get(path)
        get_response_without_pk = self.client.get(path_without_pk)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response_without_pk.status_code, 200)
        self.assertContains(get_response, 'My Profile')
        self.assertContains(get_response_without_pk, 'My Profile')
        for field in [field for field in ACCOUNT_DISPLAY_FIELDS if field != 'date_joined']:
            user_attr = getattr(self.user, field)
            if user_attr:
                self.assertContains(get_response, user_attr)
        self.assertNotContains(get_response, 'Log In')
        self.assertTemplateUsed(get_response, 'account/user_detail.html')
        self.client.logout()

    def test_user_profile_update_view_for_test_passed_user(self):
        self.client.force_login(self.user)
        path = reverse('account_user_update', kwargs={'pk': self.user.pk})
        path_without_pk = reverse('account_user_update')
        get_response = self.client.get(path)
        get_response_without_pk = self.client.get(path_without_pk)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response_without_pk.status_code, 200)
        self.assertContains(get_response, 'Update Profile')
        self.assertContains(get_response_without_pk, 'Update Profile')
        self.assertContains(get_response, self.user.username)
        self.assertNotContains(get_response, 'Log In')
        self.assertTemplateUsed(get_response, 'account/user_update.html')
        post_response = self.client.post(path, data={'first_name': 'user'})
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, self.user.get_absolute_url())
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'user')
        self.client.logout()


class UserAddressTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.address = UserAddress.objects.create(
            user=self.user,
            receiver_first_name='Rauf',
            receiver_last_name='Masoumi',
            receiver_phone_number='09019860448',
            country='Iran',
            city='Urmia',
            street='Modarress',
            no=54,
            postal_code='7737248725'
        )

    def test_user_address_creation(self):
        self.assertEqual(UserAddress.objects.count(), 1)
        self.assertEqual(UserAddress.objects.all()[0], self.address)
        self.assertEqual(self.address.receiver_first_name, 'Rauf')
        self.assertEqual(self.address.receiver_last_name, 'Masoumi')

    def test_user_address_list_view_for_test_passed_user(self):
        self.client.force_login(self.user)
        path = reverse('account_user_address_list', kwargs={'user_pk': self.user.pk})
        path_without_pk = reverse('account_user_address_list')
        response = self.client.get(path)
        response_without_pk = self.client.get(path_without_pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_without_pk.status_code, 200)
        self.assertContains(response, 'My Addresses')
        self.assertContains(response_without_pk, 'My Addresses')
        self.assertContains(response, self.address.receiver_first_name)
        self.assertNotContains(response, 'Hello im here')
        self.assertTemplateUsed(response, 'account/user_address_list.html')
        self.client.logout()

    def test_user_address_create_view(self):
        self.client.force_login(self.user)
        path = reverse('account_user_address_create')
        address_list_path = reverse('account_user_address_list')
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Create Address')
        self.assertTemplateUsed(get_response, 'account/user_address_create.html')
        post_data = {'receiver_first_name': 'Mohammad', 'receiver_last_name': 'Hello',
                     'receiver_phone_number': '0901', 'country': 'America', 'city': 'LA', 'street': 'Human',
                     'no': 35, 'postal_code': '35356'}
        post_response = self.client.post(path, post_data)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, address_list_path)
        self.assertEqual(UserAddress.objects.count(), 2)
        created_address = UserAddress.objects.all()[1]
        self.assertEqual(created_address.user, self.user)
        self.assertEqual(created_address.receiver_first_name, 'Mohammad')
        created_address.delete()
        self.client.logout()

    def test_user_address_update_view_for_test_passed_user(self):
        self.client.force_login(self.user)
        path = reverse('account_user_address_update', kwargs={'pk': self.address.pk})
        address_list_path = reverse('account_user_address_list')
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Update Address')
        self.assertContains(get_response, self.address.receiver_last_name)
        self.assertNotContains(get_response, 'Create Address')
        self.assertTemplateUsed(get_response, 'account/user_address_update.html')
        post_data = {'receiver_first_name': 'Rauf', 'receiver_last_name': 'Hello',
                     'receiver_phone_number': '09019860448', 'country': 'America', 'city': 'LA', 'street': 'Human',
                     'no': 35, 'postal_code': '35356'}
        post_response = self.client.post(path, post_data)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, address_list_path)
        self.address.refresh_from_db()
        self.assertEqual(self.address.receiver_last_name, 'Hello')
        self.client.logout()

    def test_user_address_delete_view_for_test_passed_user(self):
        self.client.force_login(self.user)
        path = reverse('account_user_address_delete', kwargs={'pk': self.address.pk})
        address_list_path = reverse('account_user_address_list')
        get_response = self.client.get(path)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Delete Address')
        self.assertNotContains(get_response, 'Update Address')
        self.assertTemplateUsed(get_response, 'account/user_address_delete.html')
        delete_response = self.client.delete(path)
        self.assertEqual(delete_response.status_code, 302)
        self.assertRedirects(delete_response, address_list_path)
        self.assertEqual(UserAddress.objects.count(), 0)
        self.client.logout()
