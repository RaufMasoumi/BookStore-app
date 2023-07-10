from django.shortcuts import render
from django.views.generic import TemplateView
from books.models import Book
from books.views import PageLocation
from accounts.views import ACCOUNT_PAGE_LOCATION_LIST
# Create your views here.


class HomePageView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sales'] = Book.objects.sale().order_by('time_to_sell')
        context['new_arrivals'] = Book.objects.new()
        context['bestsellers'] = Book.objects.bestseller().order_by('price')
        context['fast_view_books'] = context['sales'] | context['new_arrivals'] | context['bestsellers']
        return context


class AboutPageView(TemplateView):
    template_name = 'pages/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        about_location = [PageLocation('About', 'about', True)]
        context['page_location_list'] = ACCOUNT_PAGE_LOCATION_LIST + about_location
        return context


class AccountPageView(TemplateView):
    template_name = 'pages/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = ACCOUNT_PAGE_LOCATION_LIST
        return context


class CheckoutView(TemplateView):
    template_name = 'pages/checkout.html'


class ContactsPageView(TemplateView):
    template_name = 'pages/contacts.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contacts_location = [PageLocation('Contacts', 'contacts', True)]
        context['page_location_list'] = ACCOUNT_PAGE_LOCATION_LIST + contacts_location
        return context


class FaqPageView(TemplateView):
    template_name = 'pages/faq.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faq_location = [PageLocation('Frequently Asked Questions', 'faq', True)]
        context['page_location_list'] = ACCOUNT_PAGE_LOCATION_LIST + faq_location
        return context


class PrivacyPolicyPageView(TemplateView):
    template_name = 'pages/privacy_policy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        privacy_location = [PageLocation('Privacy and Policy', 'privacy', True)]
        context['page_location_list'] = ACCOUNT_PAGE_LOCATION_LIST + privacy_location
        return context


class TermsConditionsPageView(TemplateView):
    template_name = 'pages/terms_conditions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        terms_location = [PageLocation('Terms and Conditions', 'terms', True)]
        context['page_location_list'] = ACCOUNT_PAGE_LOCATION_LIST + terms_location
        return context
