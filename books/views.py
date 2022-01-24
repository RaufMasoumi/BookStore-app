from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden, HttpResponse
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from uuid import UUID
from .models import Book, Review, ReviewReply
from .forms import ReviewForm, ReviewReplyForm
# Create your views here.


class BookListView(LoginRequiredMixin, ListView):
    model = Book
    context_object_name = 'book_list'
    template_name = 'books/book_list.html'
    login_url = 'account_login'


class BookDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Book
    context_object_name = 'book'
    template_name = 'books/book_detail.html'
    login_url = 'account_login'
    permission_required = 'books.special_status'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review_form = ReviewForm(initial={'book': self.object})
        review_reply_form = ReviewReplyForm()
        context['review_form'] = review_form
        context['review_reply_form'] = review_reply_form
        return context


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    template_name = 'books/book_create.html'
    login_url = 'account_login'
    permission_required = 'books.add_book'


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    template_name = 'books/book_update.html'
    login_url = 'account_login'
    permission_required = 'books.change_book'


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/book_delete.html'
    login_url = 'account_login'
    success_url = reverse_lazy('book_list')
    permission_required = 'books.delete_book'


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    fields = ('book', 'review')
    template_name = 'books/reviews/review_create.html'
    login_url = 'account_login'

    def form_valid(self, form):
        form.instance.author = self.request.user
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
        if obj.author == self.request.user or self.request.user.has_perm('books.change_review'):
            return True
        else:
            return False


class ReviewReplyCreateView(LoginRequiredMixin, CreateView):
    model = ReviewReply
    fields = ('review', 'reply')
    template_name = 'books/reviews/replies/review_reply_create.html'
    login_url = 'account_login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        if self.request.POST.get('review_pk'):
            form.instance.review = Review.objects.get(pk=self.request.POST.get('review_pk'))
        return super().form_valid(form)


class ReviewReplyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ReviewReply
    fields = ('reply', )
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
        query = self.request.GET.get('q')
        return Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))


# is not in using
@require_POST
@login_required(login_url='account_login')
def create_review(request):
    book = Book.objects.get(id=request.META['HTTP_REFERER'].split('/')[-2])
    if int(request.POST['author']) != request.user.id or UUID(request.POST['book']) != book.id:
        return HttpResponseForbidden('<h1>401 Forbidden!</h1>')
    form = ReviewForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect(request.META['HTTP_REFERER'])

    return HttpResponse('<h1>409 Error when submitting the review!<409>', status=409)




