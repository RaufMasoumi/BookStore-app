from django.shortcuts import render
from django.views.generic import TemplateView
from books.forms import BookSearchForm
from books.models import Book, Category
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

class AccountView(TemplateView):
    template_name = 'newtemplates/shop-account.html'

class CheckoutView(TemplateView):
    template_name = 'newtemplates/shop-checkout.html'

class ContenctsView(TemplateView):
    template_name = 'newtemplates/shop-contacts.html'

class FaqView(TemplateView):
    template_name = 'newtemplates/shop-faq.html'

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
        context['category_list'] = [category for category in Category.objects.active()]
        return context

class ItemView(TemplateView):
    template_name = 'newtemplates/shop-item.html'

class PrivacyPolicyView(TemplateView):
    template_name = 'newtemplates/shop-privacy-policy.html'

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

class WishListView(TemplateView):
    template_name = 'newtemplates/shop-wishlist.html'