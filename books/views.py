from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.forms.models import model_to_dict
from .models import Book, Category, Review, ReviewReply
from .forms import BookImageFormSet, BookMakePublishedForm, ReviewForm, ReviewReplyForm
# Create your views here.


class BookListView(ListView):
    queryset = Book.objects.published()
    context_object_name = 'book_list'
    template_name = 'books/book_list.html'


class DraftBookListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    queryset = Book.objects.drafted()
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
        display_fields = ('author', 'pages', 'subject', 'rating', 'age_range', 'grade_range', 'page_size',
                          'length', 'width', 'summary')
        book_fields = {field.name: getattr(self.object, field.name) for field in self.object._meta.get_fields()
                      if field.name in display_fields}
        category_dict = {}
        book_categories = [category for category in self.object.category.all()]
        for category in Category.objects.active():
            make_active(category, book_categories, category_dict)

        book_fields['category'] = book_categories
        review_form = ReviewForm(initial={'book': self.object.pk})
        review_reply_form = ReviewReplyForm()
        context['category_dict'] = category_dict
        context['book_fields'] = book_fields
        context['review_form'] = review_form
        context['review_reply_form'] = review_reply_form
        return context


class DraftBookDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    queryset = Book.objects.drafted()
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
    context_object_name = 'category_list'


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'books/category/category_detail.html'


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
    context_object_name = 'book_list'
    template_name = 'books/search_results.html'

    def get_queryset(self):
        search_query = search_by_title_author(self.request)
        price_limit_query = price_limit(search_query, self.request)
        available_limit_query = available_limit(price_limit_query, self.request)
        published_limit_query = published_limit(available_limit_query, self.request)
        return published_limit_query


def search_by_title_author(request):
    query = request.GET.get('search')
    elem = []
    if request.GET.get('title'):
        elem.append('title')
    if request.GET.get('author'):
        elem.append('author')

    if len(elem) == 2 or len(elem) == 0:
        return Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))

    elif len(elem) == 1:
        if elem[0] == 'title':
            return Book.objects.filter(Q(title__icontains=query))
        elif elem[0] == 'author':
            return Book.objects.filter(Q(author__icontains=query))
    return


def price_limit(query, request):
    more = None
    less = None
    if request.GET.get('more'):
        more = request.GET.get('more')

    if request.GET.get('less'):
        less = request.GET.get('less')

    if not more and not less:
        return query

    elif more and less:
        price_range = (more, less)
        return query.filter(price__range=price_range)

    elif more:
        return query.filter(price__gt=more)

    elif less:
        return query.filter(price__lt=less)


def available_limit(query, request):
    if request.GET.get('available'):
        return query.filter(stock__gt=0)
    else:
        return query


def published_limit(query, request):
    if request.user.has_perm('books.spacial_status'):
        return query
    else:
        return query.objects.published()


@require_POST
@login_required(login_url='account_login')
def update_votes(request):

    if request.POST.get('positive'):
        pos_vote = True
    else:
        pos_vote = False

    if request.POST.get('review'):
        review = Review.objects.get(pk=request.POST.get('review'))
        if pos_vote:
            review.votes += 1
        else:
            review.votes -= 1
        review.save()
        return redirect(reverse('book_detail', kwargs={'pk': review.book.pk}))

    if request.POST.get('reply'):
        reply = ReviewReply.objects.get(pk=request.POST.get('reply'))
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
    if request.POST.get('book') and request.POST.get('publish'):
        book = Book.objects.get(pk=request.POST.get('book'))
        if request.POST.get('publish') == 'on':
            book.status = 'p'
            book.save()
            return redirect(reverse('draft_book_list'))

    return HttpResponseBadRequest('There was a problem in publishing the book!')


def make_active(category, check_list, save_dict, from_child=False):
    if category in check_list or from_child:
        if category.parent:
            save_dict[category] = True
            print(dictt)
            print(category.title, category.parent)
            make_active(category.parent, check_list, save_dict, from_child=True)
        else:
            save_dict[category] = True

    elif category not in save_dict.keys():
        save_dict[category] = False

    return save_dict
# @require_POST
# @login_required(login_url='account_login')
# def create_review(request):
#     book = Book.objects.get(id=request.META['HTTP_REFERER'].split('/')[-2])
#     if int(request.POST['author']) != request.user.id or UUID(request.POST['book']) != book.id:
#         return HttpResponseForbidden('<h1>401 Forbidden!</h1>')
#     form = ReviewForm(request.POST)
#     if form.is_valid():
#         form.save()
#         return redirect(request.META['HTTP_REFERER'])
#
#     return HttpResponse('<h1>409 Error when submitting the review!<409>', status=409)
