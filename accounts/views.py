from distutils.log import Log
from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.views.generic import UpdateView, DetailView, ListView, CreateView, DeleteView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from decimal import Decimal
from books.models import Book, Category
from books.views import PageLocation
from .models import UserAddress, UserCart, UserWish, UserCartBooksNumber
# Create your views here.

class UserProfileDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'account/user_detail.html'
    login_url = 'account_login'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return get_user_model().objects.get(pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        display_fields = ('username', 'first_name', 'last_name', 'phone_number',
                          'card_number', 'date_joined')
        unsorted_profile_fields = {}
        for field in self.object._meta.get_fields():
            if field.name in display_fields:
                field_name = field.name
                value = getattr(self.object, field_name)
                if value:
                    unsorted_profile_fields[field_name] = value
                else:
                    unsorted_profile_fields[field_name] = ''

        sorted_readable_profile_fields = {field.replace('_', ' '): unsorted_profile_fields.get(field) for field in display_fields}
        context['profile_fields'] = sorted_readable_profile_fields
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'),
                                         PageLocation('Profile', 'account_user_detail', True)]
        return context

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    fields = ('first_name', 'last_name', 'image', 'phone_number', 'card_number')
    template_name = 'account/user_update.html'
    success_url = reverse_lazy('home')
    login_url = 'account_login'

    def get_object(self, queryset=None):
        return get_user_model().objects.get(pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'),
                                             PageLocation('Profile', 'account_user_detail'), PageLocation('Update', 'account_user_profile_update', True)]
        return context


class UserAddressListView(LoginRequiredMixin, ListView):
    model = UserAddress
    context_object_name = 'address_list'
    login_url = 'account_login'
    template_name = 'account/user_address_list.html'

    def get_queryset(self):
        self.user = get_object_or_404(get_user_model(), pk=self.kwargs['user_pk'] 
            if self.kwargs.get('user_pk') else self.request.user.pk)
        queryset = UserAddress.objects.get(user=self.user) if UserAddress.objects.filter(user=self.user).exists() else None
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'),
                                                PageLocation('Address', 'account_user_address_list', True)]
        return context

class UserAddressCreateView(LoginRequiredMixin, CreateView):
    model = UserAddress
    fields = ('address',)
    login_url = 'account_login'
    success_url = reverse_lazy('account_user_address_list')
    template_name = 'account/user_address_create.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'),
                                                PageLocation('Address', 'account_user_address_list'), PageLocation('Create', 'account_user_address_create', True)]
        return context

class UserAddressUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserAddress
    fields = ('address',)
    login_url = 'account_login'
    success_url = reverse_lazy('account_user_address_list')
    template_name = 'account/user_address_update.html'
    
    def test_func(self):
        obj = self.get_object()
        return True if obj.user == self.request.user else False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'),
                                                PageLocation('Address', 'account_user_address_list'), PageLocation('Update', 'account_user_address_update', True)]
        return context

class UserAddressDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = UserAddress
    login_url = 'account_login'
    success_url = reverse_lazy('account_user_address_list')
    template_name = 'account/user_address_delete.html'

    def test_func(self):
        obj = self.get_object()
        return True if obj.user == self.request.user else False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'),
                                                PageLocation('Address', 'account_user_address_list'), PageLocation('Delete', 'account_user_address_delete', True)]
        return context

class UserCartDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = UserCart
    context_object_name = 'cart'
    login_url = 'account_login'
    template_name = 'newtemplates/shop-shopping-cart.html'

    def get_object(self, queryset=None):
        return super().get_object() if self.kwargs.get('pk') else UserCart.objects.get(user=self.request.user)

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user.cart

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_price'] = calculate_user_cart_total_price(self.object)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'), 
                                            PageLocation('Shopping Cart', 'account_user_cart_detail', True)]
        context['has_down_suggestions'] = True
        return context


class UserWishDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = UserWish
    context_object_name = 'wish_list'
    login_url = 'account_login'
    template_name = 'newtemplates/shop-wishlist.html'

    def get_object(self, queryset=None):
        return super().get_object() if self.kwargs.get('pk') else UserWish.objects.get(user=self.request.user)

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user.wish_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'),
                                         PageLocation('My WishList', 'account_user_wishlist_detail', True)]
        context['has_down_suggestions'] = True
        return context


@require_POST
@login_required()
def user_cart_update_view(request):
    try:
        url = request.META['HTTP_REFERER']
    except KeyError:
        url = reverse('account_user_cart_detail', kwargs={'pk': request.user.cart.pk})

    if request.POST.get('quantity') and not request.POST.get('delete'):
        quantity = int(request.POST.get('quantity'))

        if request.POST.get('book'):
            book = Book.objects.get(id=request.POST.get('book'))
            user_cart = get_object_or_404(UserCart, user=request.user)

            if not book.is_published():
                return HttpResponseBadRequest('The book is not published!')

            if book.stock >= quantity:
                user_cart.books.add(book)
                user_cart.save()
                if UserCartBooksNumber.objects.filter(book=book).exists():
                    book_number = UserCartBooksNumber.objects.get(book=book)
                else:
                    return HttpResponse('<h1>409 There was a in adding the book to the Cart</h1>')
                book_number.number = quantity
                book_number.save()
                book.stock -= quantity
                book.save()
                return redirect(url)
            else:
                return HttpResponse('<h1>409 The book has not enough stock!</h1>', status=409)

        elif request.POST.get('number'):
            number = UserCartBooksNumber.objects.get(id=request.POST.get('number'))
            book = number.book

            if not book.is_published():
                return HttpResponseBadRequest('409 <h1>The book is not published!</h1>')

            book.stock += number.number
            if book.stock >= quantity:
                number.number = quantity
                number.save()
                book.stock -= quantity
                book.save()
                return redirect(url)
            else:
                return HttpResponse('<h1>409 The book has not enough stock!', status=409)

    elif request.POST.get('add'):
        number_id = request.POST.get('add')
        number = get_object_or_404(UserCartBooksNumber, id=number_id)

        if number.cart.user != request.user:
            return HttpResponseForbidden('<h1>403 Forbidden</h1>')

        book = number.book
        if book.is_available():
            number.number += 1
            number.save()
            book.stock -= 1
            book.save()
            return redirect(url)
        else:
            return HttpResponse('<h1>409 The book has not enough stock!', status=409)

    elif request.POST.get('reduce'):
        number_id = request.POST.get('reduce')
        number = get_object_or_404(UserCartBooksNumber, id=number_id)

        if number.cart.user != request.user:
            return HttpResponseForbidden('<h1>403 Forbidden</h1>')
        number.number -= 1
        number.save()
        number.book.stock += 1
        number.book.save()
        return redirect(url)

    elif request.POST.get('delete'):
        number_id = request.POST.get('delete')
        number = get_object_or_404(UserCartBooksNumber, id=number_id)
        book = number.book
        cart = number.cart
        if cart.user != request.user:
            return HttpResponseForbidden('<h1>403 Forbidden</h1>')
        book.stock += number.number
        book.save()
        cart.books.remove(book)
        cart.save()
        return redirect(url)

    elif request.POST.get('book_add'):
        book_id = request.POST.get('book_add')
        book = get_object_or_404(Book, id=book_id)
        if not book.is_published():
            return HttpResponseBadRequest('The book is not published!')
        user_cart = UserCart.objects.get(user=request.user)
        if book.is_available():
            user_cart.books.add(book)
            user_cart.save()
            book.stock -= 1
            book.save()
            return redirect(url)
        else:
            return HttpResponse('<h1>409 The book has not enough stock!', status=409)

    else:
        return HttpResponse('<h1>409 Error when adding the book to user cart!</h1>', status=409)


@require_POST
@login_required()
def user_wish_update_view(request):
    try:
        url = request.META['HTTP_REFERER']
    except ValueError:
        url = reverse('account_user_wishlist_detail')
        
    if request.POST.get('wish_id'):
        wish_id = request.POST.get('wish_id')
        wish = get_object_or_404(UserWish, id=wish_id)

        if not wish.user == request.user:
            return HttpResponseForbidden('<h1>403 Forbidden<h1>')
    else:
        wish = request.user.wish_list

    book_id = request.POST.get('book_id')
    book = get_object_or_404(Book, id=book_id)

    if request.POST.get('add'):
        if book.is_published():
            wish.books.add(book)
        else:
            return HttpResponseBadRequest('<h1>409 The book is not published!</h1>')

    if request.POST.get('delete'):
        if wish.books.filter(pk=book.pk).exists():
            wish.books.remove(book)
        else:
            return HttpResponseBadRequest('<h1>409 The book is not in user wishlist</h1>')

    wish.save()
    return redirect(url)

def calculate_user_cart_total_price(user_cart):
    total_price = Decimal('00.00')
    for book in user_cart.books.all():
        total_price += book.price * UserCartBooksNumber.objects.get(cart=user_cart, book=book).number
    return total_price
