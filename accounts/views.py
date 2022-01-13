from django.shortcuts import render
from django.views.generic import UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import UserProfileUpdateForm
# Create your views here.


class UserProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = get_user_model()
    fields = ('first_name', 'last_name', 'image', 'phone_number', 'address', 'card_number')
    template_name = 'account/user_update.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('account_login')

    def test_func(self):
        obj = self.get_object()
        return obj.username == self.request.user.username

