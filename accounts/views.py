from django.shortcuts import render, redirect
from django.views.generic import UpdateView, DetailView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseForbidden, HttpResponse
from decimal import Decimal
from books.models import Book
from .models import UserCart, UserCartBooksNumber
# Create your views here.


class UserProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = get_user_model()
    fields = ('first_name', 'last_name', 'image', 'phone_number', 'address', 'card_number')
    template_name = 'account/user_update.html'
    success_url = reverse_lazy('home')
    login_url = 'account_login'

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user


class UserCartDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = UserCart
    context_object_name = 'cart'
    login_url = 'account_login'
    template_name = 'account/user_cart_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_price'] = calculate_user_cart_total_price(self.object)
        return context

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user


@require_POST
@login_required(login_url='account_login')
def user_cart_update_view(request):
    try:
        url = request.META['HTTP_REFERER']
    except KeyError:
        url = reverse('account_user_cart_detail', kwargs={'pk': request.user.carts.pk})

    if request.POST.get('add'):
        number_id = request.POST.get('add')
        number = UserCartBooksNumber.objects.get(id=number_id)
        if number.cart.user != request.user:
            return HttpResponseForbidden('<h1>403 Forbidden</h1>')

        book = number.book
        if book.stock > 0:
            number.number += 1
            number.save()
            book.stock -= 1
            book.save()
            return redirect(url)
        else:
            return HttpResponse('<h1>409 The book has not enough stock!', status=409)

    elif request.POST.get('reduce'):
        number_id = request.POST.get('reduce')
        number = UserCartBooksNumber.objects.get(id=number_id)
        if number.cart.user != request.user:
            return HttpResponseForbidden('<h1>403 Forbidden</h1>')
        number.number -= 1
        number.save()
        number.book.stock += 1
        number.book.save()
        return redirect(url)

    elif request.POST.get('delete'):
        number_id = request.POST.get('delete')
        number = UserCartBooksNumber.objects.get(id=number_id)
        book = number.book
        cart = number.cart
        if cart.user != request.user:
            return HttpResponseForbidden('<h1>403 Forbidden</h1>')
        book.stock += number.number
        book.save()
        cart.cart.remove(book)
        cart.save()
        return redirect(url)

    elif request.POST.get('book_add'):
        print('hello')
        book_id = request.POST.get('book_add')
        book = Book.objects.get(id=book_id)
        user_cart = UserCart.objects.get(user=request.user)
        if book.stock > 0:
            user_cart.cart.add(book)
            user_cart.save()
            book.stock -= 1
            book.save()
            return redirect(url)
        else:
            return HttpResponse('<h1>409 The book has not enough stock!', status=409)

    else:
        return HttpResponse('<h1>409 Error when adding the book to user cart!</h1>', status=409)


def calculate_user_cart_total_price(user_cart):
    total_price = Decimal('00.00')
    for book in user_cart.cart.all():
        total_price += book.price * UserCartBooksNumber.objects.get(cart=user_cart, book=book).number
    return total_price
