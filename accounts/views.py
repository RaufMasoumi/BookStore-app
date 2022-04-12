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
        if not self.kwargs.get('pk'):
            pk = self.request.user.pk
            return get_object_or_404(get_user_model(), pk=pk)
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        display_fields = ('username', 'first_name', 'last_name', 'phone_number',
                          'card_number', 'date_joined')
        unsorted_profile_fields = {}
        for field in self.object._meta.get_fields():
            if field.name in display_fields:
                field_name = field.name
                value = getattr(self.object, field_name)
                unsorted_profile_fields[field_name] = value if value else ''

        sorted_readable_profile_fields = {field.replace('_', ' '): unsorted_profile_fields.get(field) for field in display_fields}
        context['profile_fields'] = sorted_readable_profile_fields
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'),
                                         PageLocation('Profile', 'account_user_detail', True)]
        return context

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user


class UserProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'account/user_update.html'
    login_url = 'account_login'
    fields = ('first_name', 'last_name', 'image', 'phone_number', 'card_number')

    def get_object(self, queryset=None):
        if not self.kwargs.get('pk'):
            pk = self.request.user.pk
            return get_object_or_404(get_user_model(), pk=pk)
        return super().get_object(queryset)

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user 

    def get_success_url(self):
        obj = self.get_object()
        return obj.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'),
                                             PageLocation('Profile', 'account_user_detail'), PageLocation('Update', 'account_user_profile_update', True)]
        return context


class UserAddressListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = UserAddress
    context_object_name = 'address_list'
    login_url = 'account_login'
    template_name = 'account/user_address_list.html'

    def get_queryset(self):
        pk = self.kwargs['user_pk'] if self.kwargs.get('user_pk') else self.request.user.pk
        user = get_object_or_404(get_user_model(), pk=pk)
        queryset = UserAddress.objects.filter(user=user)
        return queryset
    
    def test_func(self):
        if self.kwargs.get('user_pk'):
            self.request.user.pk == self.kwargs['user_pk']
        else:
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'),
                                                PageLocation('Address', 'account_user_address_list', True)]
        return context

class UserAddressCreateView(LoginRequiredMixin, CreateView):
    model = UserAddress
    fields = ('reciever_first_name', 'reciever_last_name', 'reciever_phone_number', 'country', 'city', 'street', 'no', 'postal_code')
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
    fields = ('reciever_first_name', 'reciever_last_name', 'reciever_phone_number', 'country', 'city', 'street', 'no', 'postal_code')
    login_url = 'account_login'
    success_url = reverse_lazy('account_user_address_list')
    template_name = 'account/user_address_update.html'
    
    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user

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
        return obj.user == self.request.user

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
        if not self.kwargs.get('pk'):
            return UserCart.objects.get(user=self.request.user)
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
    template_name = 'newtemplates/shop-wishlist.html'

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
                book_number = get_object_or_404(UserCartBooksNumber, book=book)
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

    # elif post.get('add'):
    #     number = get_object_or_404(UserCartBooksNumber, pk=post.get('number_id'))

    #     if number.cart.user != request.user:
    #         return HttpResponseForbidden('<h1>403 Forbidden</h1>')

    #     book = number.book
    #     if book.is_available():
    #         number.number += 1
    #         number.save()
    #         book.stock -= 1
    #         book.save()
    #         return redirect(url)
    #     else:
    #         return HttpResponse('<h1>409 The book has not enough stock!', status=409)

    # elif post.get('reduce'):
    #     number = get_object_or_404(UserCartBooksNumber, pk=post.get('reduce'))

    #     if number.cart.user != request.user:
    #         return HttpResponseForbidden('<h1>403 Forbidden</h1>')
    #     number.number -= 1
    #     number.save()
    #     number.book.stock += 1
    #     number.book.save()
    #     return redirect(url)

    elif post.get('delete'):
        number = get_object_or_404(UserCartBooksNumber, pk=post.get('delete'))
        book = number.book
        cart = number.cart
        if cart.user != request.user:
            return HttpResponseForbidden('<h1>403 Forbidden</h1>')
        book.stock += number.number
        book.save()
        cart.books.remove(book)
        cart.save()
        return redirect(url)

    elif post.get('book_add'):
        book = get_object_or_404(Book, pk=post.get('book_add'))

        if not book.is_published():
            return HttpResponseBadRequest('The book is not published!')

        user_cart = request.user.cart
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
        url = request.user.wish_list.get_absolute_url()
        
    post = request.POST

    if post.get('wish_id'):
        wish = get_object_or_404(UserWish, pk=post['wish_id'])

        if not wish.user == request.user:
            return HttpResponseForbidden('<h1>403 Forbidden<h1>')
    else:
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
