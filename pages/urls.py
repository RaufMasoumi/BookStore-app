from django.urls import path
from .views import HomePageView, AboutPageView, AccountPageView, CheckoutView, ContactsPageView, FaqPageView, \
    PrivacyPolicyPageView, TermsConditionsPageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('account/', AccountPageView.as_view(), name='account'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('contacts/', ContactsPageView.as_view(), name='contacts'),
    path('faq/', FaqPageView.as_view(), name='faq'),
    path('privacy-policy/', PrivacyPolicyPageView.as_view(), name='privacy_policy'),
    path('terms-conditions/', TermsConditionsPageView.as_view(), name='terms_conditions'),
]