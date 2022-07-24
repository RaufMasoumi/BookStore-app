from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.generic import DetailView
from books.models import Book
from books.views import PageLocation
from .models import UserCart, UserWish, UserCartBooksNumber
# Create your views here.


class UserCartDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = UserCart
    context_object_name = 'cart'
    login_url = 'account_login'
    template_name = 'carts/user_cart_detail.html'

    def get_object(self, queryset=None):
        if not self.kwargs.get('pk'):
            return self.request.user.cart
        return super().get_object(queryset)

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user.cart

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'), 
                                         PageLocation('Shopping Cart', 'account_user_cart_detail', True)]
        context['has_down_suggestions'] = True
        return context


class UserWishDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = UserWish
    context_object_name = 'wish_list'
    login_url = 'account_login'
    template_name = 'carts/user_wishlist_detail.html'

    def get_object(self, queryset=None):
        if not self.kwargs.get('pk'):
            return UserWish.objects.get(user=self.request.user)
        return super().get_object(queryset)

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user.wish_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'),
                                         PageLocation('WishList', 'account_user_wishlist_detail', True)]
        context['has_down_suggestions'] = True
        return context


@require_POST
@login_required()
def user_cart_update_view(request):
    try:
        url = request.META['HTTP_REFERER']
    except KeyError:
        url = request.user.cart.get_absolute_url()

    post = request.POST
    if post.get('quantity') and not post.get('delete'):
        quantity = int(post.get('quantity'))

        if post.get('book'):
            book = get_object_or_404(Book, pk=post['book'])
            user_cart = request.user.cart

            if not book.is_published():
                return HttpResponseBadRequest('The book is not published!')

            if book.stock >= quantity:
                user_cart.books.add(book)
                user_cart.save()
                book_number = UserCartBooksNumber.objects.get(cart=user_cart, book=book)
                book_number.number = quantity
                book_number.save()
                book.stock -= quantity
                book.save()
                return redirect(url)
            else:
                return HttpResponse('<h1>409 The book has not enough stock!</h1>', status=409)

        elif post.get('number'):
            number = get_object_or_404(UserCartBooksNumber, pk=post['number'])
            book = number.book

            if number.cart.user != request.user:
                return HttpResponseForbidden('<h1>403 Forbidden!</h1>')

            book.stock += number.number
            if book.stock >= quantity:
                number.number = quantity
                number.save()
                book.stock -= quantity
                book.save()
                return redirect(url)
            else:
                return HttpResponse('<h1>409 The book has not enough stock!', status=409)

    elif post.get('book_add'):
        book = get_object_or_404(Book, pk=post['book_add'])
        user_cart = request.user.cart

        if not book.is_published():
            return HttpResponseBadRequest('The book is not published!')

        if book.is_available():
            user_cart.books.add(book)
            user_cart.save()
            book.stock -= 1
            book.save()
            return redirect(url)
        else:
            return HttpResponse('<h1>409 The book has not enough stock!', status=409)

    elif post.get('delete'):
        number = get_object_or_404(UserCartBooksNumber, pk=post['delete'])
        book = number.book
        cart = number.cart

        if cart.user != request.user:
            return HttpResponseForbidden('<h1>403 Forbidden</h1>')

        book.stock += number.number
        book.save()
        cart.books.remove(book)
        cart.save()
        return redirect(url)

    else:
        return HttpResponse('<h1>409 Error when adding the book to user cart!</h1>', status=409)


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
