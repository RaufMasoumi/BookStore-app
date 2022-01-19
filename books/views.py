from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden, HttpResponse
from django.urls import reverse
from django.db.models import Q
from uuid import UUID
from .models import Book, Review
from .forms import ReviewForm
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
        form = ReviewForm(initial={'author': self.request.user, 'book': self.object})
        context['review_form'] = form
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


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    fields = ('review',)
    template_name = 'books/review_update.html'
    login_url = 'account_login'

    def get_success_url(self):
        return reverse('book_detail', kwargs={'pk': self.object.book.pk})

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    login_url = 'account_login'
    template_name = 'books/review_delete.html'

    def get_success_url(self):
        return reverse('book_detail', kwargs={'pk': self.object.book.pk})

    def test_func(self):
        obj = self.get_object()
        if obj.author == self.request.user or self.request.user.has_perm('books.change_review'):
            return True
        else:
            return False


class SearchResultsView(ListView):
    model = Book
    context_object_name = 'book_list'
    template_name = 'books/search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))


@require_POST
@login_required(login_url='account_login')
def save_review(request):
    book = Book.objects.get(id=request.META['HTTP_REFERER'].split('/')[-2])
    if int(request.POST['author']) != request.user.id or UUID(request.POST['book']) != book.id:
        return HttpResponseForbidden('<h1>401 Forbidden!</h1>')
    form = ReviewForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect(request.META['HTTP_REFERER'])

    return HttpResponse('<h1>409 Error when submitting the review!<409>', status=409)




