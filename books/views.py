from typing import List
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from .models import Book, Category, Review, ReviewReply
from .forms import BookImageFormSet, BookMakePublishedForm, ReviewForm, ReviewReplyForm
from uuid import UUID
import re
# Create your views here.


class BookListView(ListView):
    queryset = Book.objects.published()
    context_object_name = 'book_list'
    template_name = 'books/book_list.html'


class DraftBookListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    queryset = Book.objects.draft()
    context_object_name = 'book_list'
    template_name = 'books/draft_book_list.html'
    login_url = 'account_login'
    permission_required = 'books.special_status'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['publish_form'] = BookMakePublishedForm()
        return context


class BookDetailView(DetailView):
    queryset = Book.objects.published()
    context_object_name = 'book'
    template_name = 'newtemplates/shop-item.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        display_fields = ('author', 'pages', 'subject', 'rating', 'publisher', 'age_range', 'grade_range', 'page_size',
                          'length', 'width', 'summary')
        book_fields = {field.replace('_', ' ').capitalize(): getattr(self.object, field) for field in display_fields
                      if field in [field.name for field in self.object._meta.get_fields()]}
        active_category_set = self.object.category.active()
        book_fields['Category'] = active_category_set
        review_form = ReviewForm(initial={'book': self.object.pk})
        review_reply_form = ReviewReplyForm()
        page_location_list = [
            PageLocation('Home', 'home'), PageLocation('Store', 'index'), PageLocation('Books', 'book_list'),
            PageLocation(self.object.title, self.object.get_absolute_url, True)
        ]
        self.object.is_in_cart = is_book_in_cart(self.object, self.request.user)
        context['page_location_list'] = page_location_list
        context['active_category_set'] = active_category_set
        context['has_down_suggestions'] = True
        context['book_fields'] = book_fields
        context['review_form'] = review_form
        context['review_reply_form'] = review_reply_form
        self.object.views += 1
        self.object.save()
        return context

class DraftBookDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    queryset = Book.objects.draft()
    context_object_name = 'book'
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
        formset = BookImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if formset.is_valid():
            formset.save()
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
        formset = BookImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if formset.is_valid():
            formset.save()
        return super().form_valid(form)


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/book_delete.html'
    login_url = 'account_login'
    success_url = reverse_lazy('book_list')
    permission_required = 'books.delete_book'


class CategoryListView(ListView):
    model = Category
    template_name = 'books/category/category_list.html'

class CategoryBooksListView(ListView):
    template_name = 'newtemplates/shop-product-list.html'
    context_object_name = 'category_books'

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        self.category = Category.objects.get(pk=pk)
        queryset = self.category.books.published()
        self.availability_on_key, self.price_on_key, self.available_on_key, self.price_less_key, self.price_more_key \
            = [False, False, '', '', '']

        get = self.request.GET
        if get.get('filter'):
            if get.get('use_price'):
                queryset, self.price_less_key, self.price_more_key = price_limit(queryset, self.request)
                self.price_on_key = True

            if get.get('use_availability'):
                queryset, self.available_on_key = available_limit(queryset, self.request)
                self.availability_on_key = True


        if get.get('showing'):
            queryset, self.order_by = sort_books(queryset, self.request)
        else:
            self.order_by = None

        return queryset

    def get_paginate_by(self, *args):
        paginate_by = 9
        if self.request.GET.get('showing'):
            paginate_by = paginate_books(self.request)
        return paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['fast_view_books'] = context['category_books']
        context['active_category_set'] = make_active_category_set(self.category)
        context['available_on_key'] = self.available_on_key
        context['availability_on_key'] = self.availability_on_key
        context['price_on_key'] = self.price_on_key
        context['price_less_key'] = self.price_less_key
        context['price_more_key'] = self.price_more_key
        context['order_by'] = self.order_by
        context['paginate_by'] = self.get_paginate_by()
        return context


class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Category
    fields = '__all__'
    template_name = 'books/category/category_create.html'
    login_url = 'account_login'
    success_url = reverse_lazy('category_list')
    permission_required = 'books.add_category'


class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Category
    fields = '__all__'
    template_name = 'books/category/category_update.html'
    login_url = 'account_login'
    success_url = reverse_lazy('category_list')
    permission_required = 'books.change_category'


class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Category
    template_name = 'books/category/category_delete.html'
    login_url = 'account_login'
    success_url = reverse_lazy('category_list')
    permission_required = 'books.delete_category'


class ReviewCreateView(CreateView):
    model = Review
    fields = ('author', 'name', 'email', 'book', 'review', 'rating')
    template_name = 'books/reviews/review_create.html'

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
            form.instance.name = self.request.user.username
            form.instance.email = self.request.user.email
        return super().form_valid(form)


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    fields = ('review',)
    template_name = 'books/reviews/review_update.html'
    login_url = 'account_login'

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    login_url = 'account_login'
    template_name = 'books/reviews/review_delete.html'

    def get_success_url(self):
        return reverse('book_detail', kwargs={'pk': self.object.book.pk})

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.has_perm('books.change_review')


class ReviewReplyCreateView(LoginRequiredMixin, CreateView):
    model = ReviewReply
    fields = ('review', 'reply', 'add')
    template_name = 'books/reviews/replies/review_reply_create.html'
    login_url = 'account_login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        if self.request.POST.get('add'):
            form.instance.add = ReviewReply.objects.get(pk=self.request.POST.get('add'))
        # if self.request.POST.get('review'):
        #     form.instance.review = Review.objects.get(pk=self.request.POST.get('review'))
        return super().form_valid(form)


class ReviewReplyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ReviewReply
    fields = ('reply', 'add')
    template_name = 'books/reviews/replies/review_reply_update.html'
    login_url = 'account_login'

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class ReviewReplyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ReviewReply
    template_name = 'books/reviews/replies/review_reply_delete.html'
    login_url = 'account_login'

    def get_success_url(self):
        obj = self.get_object()
        return reverse('book_detail', kwargs={'pk': obj.review.book.pk})

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.has_perm('books.delete_reviewreply')


class SearchResultsView(ListView):
    model = Book
    context_object_name = 'search_book_list'

    def get_template_names(self):
        template_names = []
        if self.request.GET.get('come_from_comparing'):
            template_names.append('newtemplates/book_add_to_comparing_list.html')
        else:
            template_names.append('newtemplates/shop-search-result.html')
        return template_names

    def get_queryset(self):
        get = self.request.GET
        self.searched = get['query'] if get.get('query') else ''
        queryset = Book.objects.all()
        queryset = search_by_title_author(queryset, self.request)
        self.search_queryset = queryset
        queryset = published_limit(queryset, self.request)
        self.availability_on_key, self.price_on_key, self.available_on_key, self.price_less_key, self.price_more_key \
            = [False, False, '', '', '']

        if get.get('filter'):
            if get.get('use_price'):
                queryset, self.price_less_key, self.price_more_key = price_limit(queryset, self.request)
                self.price_on_key = True

            if get.get('use_availability'):
                queryset, self.available_on_key = available_limit(queryset, self.request)
                self.availability_on_key = True


        if get.get('showing'):
            queryset, self.order_by = sort_books(queryset, self.request)
        else:
            self.order_by = None
        return queryset

    def get_paginate_by(self, *args):
        paginate_by = 9
        if self.request.GET.get('showing'):
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
            books = []
            books_get_dict = {}
            pattern = 'book-'
            if get.get('book-1'):
                pattern_list = []
                for number in range(len(get)):
                    get_pattern = pattern + str(number+1)
                    pattern_list.append(get_pattern)
                for get_pattern in pattern_list:
                    if get.get(get_pattern) and Book.objects.filter(pk=get[get_pattern]).exists:
                        book = Book.objects.get(pk=get[get_pattern])
                        books.append(book)
                for index in range(len(books)):
                    books_get_dict[pattern_list[index]] = books[index].pk
            context['books_comparing_get_dict'] = books_get_dict
            context['new_book_comparing_get_pattern'] = pattern + str(len(books)+1)
        return context

class BookComparingView(TemplateView):
    template_name = 'newtemplates/shop-goods-compare.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        display_fields = ('author', 'pages', 'subject', 'rating', 'publisher', 'age_range', 'grade_range', 'page_size',
                          'length', 'width', 'summary')

        comparing_dict = {field.replace('_', ' ').capitalize():[] for field in display_fields if field in [field.name for field in Book._meta.get_fields()]}
        books = []
        pattern = 'book-'
        pattern_list = []
        get = self.request.GET
        for number in range(len(get)):
            pattern_list.append(pattern+str(number+1))

        for get_pattern in pattern_list:
            if get.get(get_pattern):
                pk = get[get_pattern]
                if Book.objects.filter(pk=pk).exists():
                    book = Book.objects.get(pk=pk)
                    book.is_in_cart = is_book_in_cart(book, self.request.user)
                    books.append(book)

        if get.get('delete_book'):
            pk = get['delete_book']
            if Book.objects.filter(pk=pk).exists():
                book = Book.objects.get(pk=pk)
                if book in books:
                    books.remove(book)

        for field in display_fields:
            for book in books:
                comparing_dict[field.replace('_', ' ').capitalize()].append(getattr(book, field))
        

        books_get_dict = {}
        for index in range(len(books)):
            books_get_dict[pattern_list[index]] = books[index].pk

        context['comparing_dict'] = comparing_dict
        context['books'] = books
        context['books_get_dict'] = books_get_dict
        context['books_count'] = len(books)
        return context

class PageLocation:
    def __init__(self, title: str, view_name: str, is_active=False):
        self.title = title
        self.view_name = view_name
        self.is_active = is_active

    def make_full_url(self):
        return reverse(self.view_name)


def search_by_title_author(queryset, request):
    get = request.GET
    query = get.get('query')
    if not query:
        return queryset
    elem = []
    if get.get('title'):
        elem.append('title')
    if get.get('author'):
        elem.append('author')

    if len(elem) == 2 or len(elem) == 0:
        queryset = queryset.filter(Q(title__icontains=query) | Q(author__icontains=query))

    elif len(elem) == 1:
        if elem[0] == 'title':
            queryset = queryset.filter(Q(title__icontains=query))
        elif elem[0] == 'author':
            queryset = queryset.filter(Q(author__icontains=query))

    return queryset


def price_limit(queryset, request):
    more = None
    less = None

    if request.GET.get('amount'):
        pattern = '\$(\d+) - \$(\d+)'
        amount = re.match(pattern,  request.GET.get('amount'))
        if not amount:
            return queryset, less, more
    else:
        return queryset, less, more

    more, less = amount.groups()

    if more and less:
        price_range = (more, less)
        queryset = queryset.filter(price__range=price_range)

    elif more:
        queryset = queryset.filter(price__gt=more)

    elif less:
        queryset = queryset.filter(price__lt=less)
    return queryset, less, more


def available_limit(queryset, request):
    on_key = ''
    get = request.GET
    if get.get('available') and not get.get('unavailable'):
        queryset = queryset.filter(stock__gt=0)
        on_key = 'available'
    elif get.get('unavailable')  and not get.get('available'):
        queryset = queryset.filter(stock__lt=1)
        on_key = 'unavailable'
    return queryset, on_key


def published_limit(queryset, request):
    if request.user.has_perm('books.spacial_status'):
        return queryset
    else:
        return queryset.filter(status='p')


def sort_books(queryset, request):
    ordering_list = {'title': 'Name (A - Z)', '-title': 'Name (Z - A)', 'price': 'Price (Low > High)',
                     '-price': 'Price (High > Low)', 'rating': 'Rating (Highest)', '-rating': 'Rating (Lowest)'}
    order_by = request.GET.get('sort')
    if order_by in ordering_list.keys():
        return queryset.order_by(order_by), {order_by: ordering_list[order_by]}
    return queryset, order_by


def paginate_books(request):
    paginate_by = request.GET.get('show')
    try:
        paginate_by = int(paginate_by)
    except ValueError:
        paginate_by = 9
    else:
        if paginate_by not in [3 * number for number in range(3, 7)]:
            paginate_by = 9

    return paginate_by


@require_POST
@login_required(login_url='account_login')
def update_votes(request):
    post = request.POST
    if post.get('positive'):
        pos_vote = True
    else:
        pos_vote = False

    if post.get('review'):
        review = Review.objects.get(pk=post['review'])
        if pos_vote:
            review.votes += 1
        else:
            review.votes -= 1
        review.save()
        return redirect(reverse('book_detail', kwargs={'pk': review.book.pk}))

    if post.get('reply'):
        reply = ReviewReply.objects.get(pk=post.get['reply'])
        if pos_vote:
            reply.votes += 1
        else:
            reply.votes -= 1
        reply.save()
        return redirect(reverse('book_detail', kwargs={'pk': reply.review.book.pk}))


@require_POST
@login_required(login_url='account_login')
@permission_required(perm='books.change_book')
def book_make_published(request):
    post = request.POST
    if post.get('book') and post.get('publish'):
        book = Book.objects.get(pk=post['book'])
        if post['publish'] == 'on':
            book.status = 'p'
            book.save()
            return redirect(reverse('draft_book_list'))

    return HttpResponseBadRequest('There was a problem in publishing the book!')


def make_active_category_set(category=None):
    active_category_set = set()
    while category:
        active_category_set.add(category)
        category = category.parent
    return active_category_set

def is_book_in_cart(book:Book, user)-> bool:
    if isinstance(book, Book):
        return True if user.cart.books.filter(pk=book.pk).exists() else False
    return False