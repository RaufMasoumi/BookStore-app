from django.shortcuts import render
from django.views.generic import TemplateView
from books.models import Book
from books.views import PageLocation
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
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'), PageLocation('About', 'about', True)]
        return context


class AccountPageView(TemplateView):
    template_name = 'pages/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account', True)]
        return context


class CheckoutView(TemplateView):
    template_name = 'pages/checkout.html'


class ContactsPageView(TemplateView):
    template_name = 'pages/contacts.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'), 
                                         PageLocation('Contacts', 'contacts', True)]
        return context


class FaqPageView(TemplateView):
    template_name = 'pages/faq.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'), 
                                         PageLocation('Frequently Asked Questions', 'faq', True)]
        return context


class PrivacyPolicyPageView(TemplateView):
    template_name = 'pages/privacy_policy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'), 
                                         PageLocation('Privacy and Policy', 'privacy', True)]
        return context


class TermsConditionsPageView(TemplateView):
    template_name = 'pages/terms_conditions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'), 
                                         PageLocation('Terms and Conditions', 'terms', True)]
        return context