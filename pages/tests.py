from django.test import TestCase, SimpleTestCase, override_settings
from django.urls import reverse, resolve
from config.settings import BASE_DIR
from .views import *
# Create your tests here.

# CCP -> CUSTOM CONTEXT PROCESSORS
# Have to delete the CCP to inherit SimpleTestCase for database reasons.
CCP_DELETED_TEMPLATES_SETTING = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR.joinpath('templates'))],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


class HomePageTests(TestCase):

    def setUp(self):
        url = reverse('home')
        self.response = self.client.get(url)

    def test_homepage_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_homepage_template(self):
        self.assertTemplateUsed(self.response, 'pages/home.html')

    def test_homepage_contains_correct_html(self):
        self.assertContains(self.response, 'Home')

    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, 'Hi there I should not be here.')

    def test_homepage_url_resolves_homepage_view(self):
        view = resolve('/')
        self.assertEqual(view.func.__name__, HomePageView.as_view().__name__)


@override_settings(TEMPLATES=CCP_DELETED_TEMPLATES_SETTING)
class AboutPageTests(SimpleTestCase):

    def setUp(self):
        url = reverse('about')
        self.response = self.client.get(url)

    def test_about_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_about_page_template(self):
        self.assertTemplateUsed(self.response, 'pages/about.html')

    def test_about_page_contains_correct_html(self):
        self.assertContains(self.response, 'About Us')

    def test_about_page_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, 'Hi there I should not be here.')

    def test_about_page_url_resolves_about_page_view(self):
        view = resolve('/about/')
        self.assertEqual(view.func.__name__, AboutPageView.as_view().__name__)


@override_settings(TEMPLATES=CCP_DELETED_TEMPLATES_SETTING)
class AccountPageTests(SimpleTestCase):

    def setUp(self):
        url = reverse('account')
        self.response = self.client.get(url)

    def test_account_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_account_page_template(self):
        self.assertTemplateUsed(self.response, 'pages/account.html')

    def test_account_page_contains_correct_html(self):
        self.assertContains(self.response, 'My Account')

    def test_account_page_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, 'Hi there I should not be here.')

    def test_account_page_url_resolves_account_page_view(self):
        view = resolve('/account/')
        self.assertEqual(view.func.__name__, AccountPageView.as_view().__name__)


@override_settings(TEMPLATES=CCP_DELETED_TEMPLATES_SETTING)
class CheckoutTests(SimpleTestCase):

    def setUp(self):
        url = reverse('checkout')
        self.response = self.client.get(url)

    def test_checkout_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_checkout_page_template(self):
        self.assertTemplateUsed(self.response, 'pages/checkout.html')

    def test_checkout_page_contains_correct_html(self):
        self.assertContains(self.response, 'Checkout')

    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, 'Hi there I should not be here.')

    def test_checkout_page_url_resolves_checkout_page_view(self):
        view = resolve('/checkout/')
        self.assertEqual(view.func.__name__, CheckoutView.as_view().__name__)


@override_settings(TEMPLATES=CCP_DELETED_TEMPLATES_SETTING)
class ContactsPageTests(SimpleTestCase):

    def setUp(self):
        url = reverse('contacts')
        self.response = self.client.get(url)

    def test_contacts_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_contacts_page_template(self):
        self.assertTemplateUsed(self.response, 'pages/contacts.html')

    def test_contacts_page_contains_correct_html(self):
        self.assertContains(self.response, 'Contacts')

    def test_contacts_page_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, 'Hi there I should not be here!!!')

    def test_contacts_page_url_resolves_contacts_page_view(self):
        view = resolve('/contacts/')
        self.assertEqual(view.func.__name__, ContactsPageView.as_view().__name__)


@override_settings(TEMPLATES=CCP_DELETED_TEMPLATES_SETTING)
class FaqPageTests(SimpleTestCase):

    def setUp(self):
        url = reverse('faq')
        self.response = self.client.get(url)

    def test_faq_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_faq_page_template(self):
        self.assertTemplateUsed(self.response, 'pages/faq.html')

    def test_faq_page_contains_correct_html(self):
        self.assertContains(self.response, 'Frequently Asked Questions')

    def test_faq_page_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, 'Hi there I should not be here.')

    def test_faq_page_url_resolves_faq_page_view(self):
        view = resolve('/faq/')
        self.assertEqual(view.func.__name__, FaqPageView.as_view().__name__)


@override_settings(TEMPLATES=CCP_DELETED_TEMPLATES_SETTING)
class PrivacyPolicyPageTests(SimpleTestCase):

    def setUp(self):
        url = reverse('privacy_policy')
        self.response = self.client.get(url)

    def test_privacy_policy_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_privacy_policy_page_template(self):
        self.assertTemplateUsed(self.response, 'pages/privacy_policy.html')

    def test_privacy_policy_page_contains_correct_html(self):
        self.assertContains(self.response, 'Privacy Policy')

    def test_privacy_policy_page_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, 'Hi there I should not be here!')

    def test_privacy_policy_page_url_resolves_privacy_policy_page_view(self):
        view = resolve('/privacy-policy/')
        self.assertEqual(view.func.__name__, PrivacyPolicyPageView.as_view().__name__)


@override_settings(TEMPLATES=CCP_DELETED_TEMPLATES_SETTING)
class TermsConditionsPageTests(SimpleTestCase):

    def setUp(self):
        url = reverse('terms_conditions')
        self.response = self.client.get(url)

    def test_terms_conditions_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_terms_conditions_page_template(self):
        self.assertTemplateUsed(self.response, 'pages/terms_conditions.html')

    def test_terms_conditions_page_contains_correct_html(self):
        self.assertContains(self.response, 'Terms &amp; Conditions')

    def test_terms_conditions_page_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, 'Hi there I should not be here!!')

    def test_terms_conditions_page_url_resolves_terms_conditions_page_view(self):
        view = resolve('/terms-conditions/')
        self.assertEqual(view.func.__name__, TermsConditionsPageView.as_view().__name__)
