from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from reviews.forms import ReviewForm
from .models import Book
from .forms import BookImageFormSet
import re
# Create your views here.

BOOK_DISPLAY_FIELDS = ('author', 'pages', 'subject', 'rating', 'publisher', 'age_range', 'grade_range', 'page_size',
                       'length', 'width', 'summary')
# key: value -> field name: human-readable field name
BOOK_DISPLAY_FIELDS_DICT = {field: field.replace('_', ' ').capitalize() for field in BOOK_DISPLAY_FIELDS}

# key: value -> order-by query: human-readable name
ORDERING_DICT = {'title': 'Name (A - Z)', '-title': 'Name (Z - A)', 'price': 'Price (Low > High)',
                 '-price': 'Price (High > Low)', 'rating': 'Rating (Highest)', '-rating': 'Rating (Lowest)'}


class BaseBookDetailView(DetailView):
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book_fields = {BOOK_DISPLAY_FIELDS_DICT[field]: getattr(self.object, field, '')
                       for field in BOOK_DISPLAY_FIELDS_DICT.keys()}
        active_category_queryset = self.object.category.active()
        book_fields['Category'] = active_category_queryset
        review_form = ReviewForm(initial={'book': self.object.pk})
        page_location_list = [
            PageLocation('Home', 'home'), PageLocation('Books', 'home'),
            PageLocation(self.object.title, self.object.get_absolute_url(), True)
        ]
        self.object.is_in_cart = self.object.is_in_cart(self.request.user)
        context['page_location_list'] = page_location_list
        context['active_category_set'] = active_category_queryset
        context['has_down_suggestions'] = True
        context['book_fields'] = book_fields
        context['review_form'] = review_form
        return context


class BookDetailView(BaseBookDetailView):
    queryset = Book.objects.published()
    template_name = 'books/book_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object.views += 1
        self.object.save()
        return context


class DraftBookDetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseBookDetailView):
    queryset = Book.objects.draft()
    template_name = 'books/draft_book_detail.html'
    login_url = 'account_login'
    permission_required = 'books.special_status'


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    template_name = 'books/book_create.html'
    login_url = 'account_login'
    permission_required = 'books.add_book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_formset'] = BookImageFormSet()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        save_image_formset(self.request, self.object)
        return response


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    template_name = 'books/book_update.html'
    login_url = 'account_login'
    permission_required = 'books.change_book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_formset'] = BookImageFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        save_image_formset(self.request, self.object)
        return response


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/book_delete.html'
    login_url = 'account_login'
    success_url = reverse_lazy('home')
    permission_required = 'books.delete_book'


class SearchResultsView(ListView):
    context_object_name = 'search_book_list'

    def get_template_names(self):
        template_names = []
        if self.request.GET.get('come_from_comparing'):
            template_names.append('books/book_add_to_comparing_list.html')
        else:
            template_names.append('books/search_results.html')
        return template_names

    def get_queryset(self):
        get = self.request.GET
        self.searched = get['query'] if get.get('query') else ''
        queryset = Book.objects.all()
        queryset = published_limit(queryset, self.request)
        queryset = search_by_title_author(queryset, self.request)
        self.search_queryset = queryset
        queryset, self.availability_on_key, self.price_on_key, self.available_on_key, self.price_less_key, \
        self.price_more_key, self.order_by = book_list_filtering_showing(queryset, self.request, published=False)
        return queryset

    def get_paginate_by(self, *args):
        paginate_by = 9
        if self.request.GET.get('showing') and self.request.GET.get('show'):
            paginate_by = paginate_books(self.request)
        return paginate_by

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fast_view_books'] = self.get_queryset()
        context['searched'] = self.searched
        context['available'] = self.search_queryset.filter(stock__gt=0).count()
        context['unavailable'] = self.search_queryset.filter(stock__lt=1).count()
        context['availability_on_key'] = self.availability_on_key
        context['price_on_key'] = self.price_on_key
        context['available_on_key'] = self.available_on_key
        context['price_less_key'] = self.price_less_key
        context['price_more_key'] = self.price_more_key
        context['order_by'] = self.order_by
        context['paginate_by'] = self.get_paginate_by()
        get = self.request.GET
        if get.get('come_from_comparing'):
            books_get_dict = make_books_get_dict(*get_books_from_comparing(get))
            new_pattern = 'book-' + str(len(books_get_dict.keys()) + 1)
            context['books_comparing_get_dict'] = books_get_dict
            context['new_book_comparing_get_pattern'] = new_pattern
        return context


class BookComparingView(TemplateView):
    template_name = 'books/book_comparing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comparing_dict = {BOOK_DISPLAY_FIELDS_DICT[field]: [] for field in BOOK_DISPLAY_FIELDS_DICT.keys()}
        get = self.request.GET
        pattern_list, books = get_books_from_comparing(get)

        if get.get('delete_book'):
            pk = get['delete_book']
            if Book.objects.filter(pk=pk).exists():
                book = Book.objects.get(pk=pk)
                if book in books:
                    books.remove(book)
                    pattern_list.pop()

        for field, human_readable_field in BOOK_DISPLAY_FIELDS_DICT.items():
            for book in books:
                comparing_dict[human_readable_field].append(getattr(book, field, ''))

        for book in books:
            book.is_in_cart = book.is_in_cart(self.request.user)

        books_get_dict = make_books_get_dict(pattern_list, books)

        context['comparing_dict'] = comparing_dict
        context['books'] = books
        context['books_get_dict'] = books_get_dict
        context['books_count'] = len(books)
        return context


@require_POST
@login_required(login_url='account_login')
@permission_required(perm='books.change_book')
def book_make_published(request):
    post = request.POST
    if post.get('book') and post.get('publish'):
        book = get_object_or_404(Book, pk=post['book'])
        if post['publish'] == 'on':
            book.status = 'p'
            book.save()
            return redirect(book.get_absolute_url())

    return HttpResponseBadRequest('There was a problem in publishing the book!')


def search_by_title_author(queryset, request):
    get = request.GET
    query = get.get('query')
    if query:
        queryset = queryset.filter(Q(title__icontains=query) | Q(author__icontains=query))
    return queryset


def price_limit(queryset, request):
    less = None
    more = None
    pattern = '\$(\d+) - \$(\d+)'
    amount = re.match(pattern, request.GET['amount'])
    if not amount:
        return queryset, less, more

    less, more = amount.groups()

    if less and more:
        less = int(less)
        more = int(more)
        price_range = (less, more)
        queryset = queryset.filter(price__range=price_range)

    return queryset, less, more


def available_limit(queryset, request):
    on_key = ''
    get = request.GET

    if get.get('available') and not get.get('unavailable'):
        queryset = queryset.filter(stock__gt=0)
        on_key = 'available'

    elif get.get('unavailable') and not get.get('available'):
        queryset = queryset.filter(stock__lt=1)
        on_key = 'unavailable'

    else:
        on_key = 'both'

    return queryset, on_key


def published_limit(queryset, request):
    if request.user.has_perm('books.spacial_status'):
        return queryset
    else:
        return queryset.filter(status='p')


def sort_books(queryset, request):
    order_by = request.GET['sort']
    if ORDERING_DICT.get(order_by):
        return queryset.order_by(order_by), {order_by: ORDERING_DICT[order_by]}
    return queryset, order_by


def paginate_books(request):
    paginate_by = request.GET['show']
    try:
        paginate_by = int(paginate_by)
    except TypeError:
        paginate_by = 9
    else:
        if paginate_by not in [3 * number for number in range(3, 7)]:
            paginate_by = 9

    return paginate_by


def book_list_filtering_showing(queryset, request, published=True, price=True, available=True, sort=True):
    get = request.GET
    availability_on_key, price_on_key, available_on_key, price_less_key, price_more_key, order_by = \
        (False, False, '', '', '', None)

    if published:
        queryset = published_limit(queryset, request)

    if get.get('filter'):
        # if view need price limit and request sent price limit data
        if price and get.get('use_price') and get.get('amount'):
            queryset, price_less_key, price_more_key = price_limit(queryset, request)
            price_on_key = True

        if available and get.get('use_availability'):
            queryset, available_on_key = available_limit(queryset, request)
            availability_on_key = True

    if sort and get.get('showing') and get.get('sort'):
        queryset, order_by = sort_books(queryset, request)

    return queryset, availability_on_key, price_on_key, available_on_key, price_less_key, price_more_key, order_by


class PageLocation:
    def __init__(self, title: str, view_name: str, is_active=False):
        self.title = title
        self.view_name = view_name
        self.is_active = is_active

    def __str__(self):
        return self.title

    def make_full_url(self):
        return reverse(self.view_name)


def is_book_in_cart(book: Book, user) -> bool:
    if isinstance(book, Book) and user.is_authenticated:
        return user.cart.books.filter(pk=book.pk).exists()
    return False


def get_books_from_comparing(get):
    books = []
    pattern_list = []
    if get.get('book-1'):
        pattern = 'book-'
        for number in range(len(get)):
            get_pattern = pattern + str(number+1)
            if get.get(get_pattern):
                pk = get[get_pattern]
                if Book.objects.filter(pk=pk).exists():
                    book = Book.objects.get(pk=pk)
                    pattern_list.append(get_pattern)
                    books.append(book)
    return pattern_list, books


def make_books_get_dict(pattern_list: list, books: list):
    get_dict = {}
    for item in zip(pattern_list, books):
        pattern, book = item
        get_dict[pattern] = book.pk
    return get_dict


def save_image_formset(request, obj):
    formset = BookImageFormSet(request.POST, request.FILES, instance=obj)
    if formset.is_valid():
        formset.save()
