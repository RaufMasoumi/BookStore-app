from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.generic import DetailView
from books.models import Book
from books.views import PageLocation
from accounts.views import ACCOUNT_PAGE_LOCATION_LIST, IsUserItselfTestMixin
from .models import UserCart, UserWish, UserCartBooksNumber
from .forms import UserCartNumberByNumberForm, UserCartNumberByBookForm, UserCartBookDeleteForm
# Create your views here.


class BaseUserCartWishDetailView(LoginRequiredMixin, IsUserItselfTestMixin, DetailView):
    login_url = 'account_login'
    queryset_field_name = ''

    def get_queryset_field_name(self):
        if self.queryset_field_name:
            return self.queryset_field_name
        else:
            return self.context_object_name

    def get_object(self, queryset=None):
        if not self.kwargs.get('pk'):
            return getattr(self.request.user, self.get_queryset_field_name(), None)
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_down_suggestions'] = True
        return context


class UserCartDetailView(BaseUserCartWishDetailView):
    model = UserCart
    context_object_name = 'cart'
    template_name = 'carts/user_cart_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_location = [PageLocation('Shopping Cart', 'account_user_cart_detail', True)]
        context['page_location_list'] = ACCOUNT_PAGE_LOCATION_LIST + cart_location
        return context


class UserWishDetailView(BaseUserCartWishDetailView):
    model = UserWish
    context_object_name = 'wish_list'
    template_name = 'carts/user_wishlist_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wish_list_location = [PageLocation('WishList', 'account_user_wishlist_detail', True)]
        context['page_location_list'] = ACCOUNT_PAGE_LOCATION_LIST + wish_list_location
        return context


@require_POST
@login_required()
def user_cart_update_view(request):
    try:
        url = request.META['HTTP_REFERER']
    except KeyError:
        url = request.user.cart.get_absolute_url()

    post = request.POST
    by_number_form = UserCartNumberByNumberForm(post)
    if by_number_form.is_valid():
        cleaned_data = by_number_form.cleaned_data
        number = get_object_or_404(UserCartBooksNumber, pk=cleaned_data.get('number_pk'))
        if number.cart.user != request.user:
            return HttpResponseForbidden('<h1>403 Forbidden</h1>')
        number.number = cleaned_data.get('quantity')
        number.save()

    by_book_form = UserCartNumberByBookForm(post)
    if by_book_form.is_valid():
        cleaned_data = by_book_form.cleaned_data
        book = get_object_or_404(Book, pk=cleaned_data.get('book_pk'))
        if not book.is_published():
            return HttpResponseForbidden('<h1>403 Forbidden. The book is not published!</h1>')
        cart = request.user.cart
        cart.books.add(book)
        cart.save()
        new_number = book.carts_numbers.get(cart=cart)
        new_number.refresh_from_db()
        quantity = cleaned_data.get('quantity')
        if quantity != 1:
            new_number.number = quantity
            new_number.save()

    book_delete_form = UserCartBookDeleteForm(post)
    if book_delete_form.is_valid():
        book = get_object_or_404(Book, pk=book_delete_form.cleaned_data.get('delete_book_pk'))
        cart = request.user.cart
        if cart.books.filter(pk=book.pk).exists:
            cart.books.remove(book)
            cart.save()

    return redirect(url)


@require_POST
@login_required()
def user_wish_update_view(request):
    try:
        url = request.META['HTTP_REFERER']
    except KeyError:
        url = request.user.wish_list.get_absolute_url()
        
    post = request.POST

    wish = request.user.wish_list

    book_id = post.get('book_id')
    book = get_object_or_404(Book, pk=book_id)

    if post.get('add'):
        if book.is_published():
            wish.books.add(book)
        else:
            return HttpResponseBadRequest('<h1>409 The book is not published!</h1>')

    if post.get('delete'):
        if wish.books.filter(pk=book.pk).exists():
            wish.books.remove(book)
        else:
            return HttpResponseBadRequest('<h1>409 The book is not in user wishlist</h1>')

    wish.save()
    return redirect(url)
