from django.shortcuts import render
from django.views.generic import TemplateView
from books.forms import BookSearchForm
from books.models import Book, Category
from books.views import PageLocation
from django.contrib.auth import get_user_model
# Create your views here.


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = BookSearchForm()
        return context


class AboutPageView(TemplateView):
    template_name = 'about.html'


def hello(request):
    return render(request, 'hello.html')

class AboutView(TemplateView):
    template_name = 'newtemplates/shop-about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'), PageLocation('About', 'about', True)]
        return context

class AccountView(TemplateView):
    template_name = 'newtemplates/shop-account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account', True)]
        return context
class CheckoutView(TemplateView):
    template_name = 'newtemplates/shop-checkout.html'

class ContenctsView(TemplateView):
    template_name = 'newtemplates/shop-contacts.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'), 
            PageLocation('Contacts', 'contacts', True)]
        return context

class FaqView(TemplateView):
    template_name = 'newtemplates/shop-faq.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'), 
            PageLocation('Frequently Asked Questions', 'faq', True)]
        return context

class GoodsView(TemplateView):
    template_name = 'newtemplates/shop-goods-compare.html'

class IndexView(TemplateView):
    template_name = 'newtemplates/shop-index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sales'] = Book.objects.sale()
        context['new_arrivals'] = Book.objects.new()
        context['bestsellers'] = Book.objects.bestseller()
        context['fast_view_books'] = context['sales'] | context['new_arrivals'] | context['bestsellers']
        return context

class ItemView(TemplateView):
    template_name = 'newtemplates/shop-item.html'

class PrivacyPolicyView(TemplateView):
    template_name = 'newtemplates/shop-privacy-policy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'), 
            PageLocation('Privacy and Policy', 'privacy', True)]
        return context

class ProductListView(TemplateView):
    template_name = 'newtemplates/shop-product-list.html'

class SearchResultView(TemplateView):
    template_name = 'newtemplates/shop-search-result.html'

class ShoppingCartView(TemplateView):
    template_name = 'newtemplates/shop-shopping-cart.html'

class ShoppingCartNullView(TemplateView):
    template_name = 'newtemplates/shop-shopping-cart-null.html'

class StandardFormsView(TemplateView):
    template_name = 'newtemplates/shop-standart-forms.html'

class TermsConditionsView(TemplateView):
    template_name = 'newtemplates/shop-terms-conditions-page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'), 
            PageLocation('Terms and Conditions', 'terms', True)]
        return context

class WishListView(TemplateView):
    template_name = 'newtemplates/shop-wishlist.html'