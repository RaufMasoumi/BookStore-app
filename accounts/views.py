from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import UpdateView, DetailView, ListView, CreateView, DeleteView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from books.views import PageLocation
from .models import UserAddress
# Create your views here.

ACCOUNT_DISPLAY_FIELDS = ('username', 'first_name', 'last_name', 'phone_number', 'card_number', 'date_joined')


class UserProfileDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = get_user_model()
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
        unsorted_profile_fields = {}
        for field in self.object._meta.get_fields():
            if field.name in ACCOUNT_DISPLAY_FIELDS:
                field_name = field.name
                value = getattr(self.object, field_name)
                unsorted_profile_fields[field_name] = value if value else ''

        sorted_readable_profile_fields = {field.replace('_', ' '): unsorted_profile_fields.get(field)
                                          for field in ACCOUNT_DISPLAY_FIELDS}
        context['profile_fields'] = sorted_readable_profile_fields
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'),
                                         PageLocation('Profile', 'account_user_detail', True)]
        return context

    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user


class UserProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = get_user_model()
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
            return self.request.user.pk == self.kwargs['user_pk']
        else:
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_location_list'] = [PageLocation('Home', 'home'), PageLocation('Account', 'account'),
                                         PageLocation('Address', 'account_user_address_list', True)]
        return context


class UserAddressCreateView(LoginRequiredMixin, CreateView):
    model = UserAddress
    fields = ('receiver_first_name', 'receiver_last_name', 'receiver_phone_number', 'country', 'city', 'street', 'no', 'postal_code')
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
    fields = ('receiver_first_name', 'receiver_last_name', 'receiver_phone_number', 'country', 'city', 'street', 'no', 'postal_code')
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
