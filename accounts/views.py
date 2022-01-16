from django.shortcuts import render, redirect
from django.views.generic import UpdateView, DetailView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from decimal import Decimal
from .models import UserCart, UserCartBooksNumber
# Create your views here.


class UserProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = get_user_model()
    fields = ('first_name', 'last_name', 'image', 'phone_number', 'address', 'card_number')
    template_name = 'account/user_update.html'
    success_url = 'home'
    login_url = 'account_login'

    def test_func(self):
        obj = self.get_object()
        return obj.username == self.request.user.username


class UserCartDetailView(LoginRequiredMixin, DetailView):
    model = UserCart
    context_object_name = 'cart'
    login_url = 'account_login'
    template_name = 'account/usercart_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_price'] = calculate_user_cart_total_price(self.object)
        return context


def user_cart_editing_view(request):
    if request.method == 'POST':
        if request.POST.get('add'):
            number_id = request.POST.get('add')
            number = UserCartBooksNumber.objects.get(id=number_id)
            number.number += 1
            number.save()
            return redirect(reverse('account_usercart_detail', args=[number.cart.pk]))

        if request.POST.get('disadd'):
            number_id = request.POST.get('disadd')
            number = UserCartBooksNumber.objects.get(id=number_id)
            number.number -= 1
            number.save()
            return redirect(reverse('account_usercart_detail', args=[number.cart.pk]))

def calculate_user_cart_total_price(user_cart):
    total_price = Decimal('00.00')
    for book in user_cart.cart.all():
        total_price += book.price * UserCartBooksNumber.objects.get(cart=user_cart, book=book).number
    return total_price
