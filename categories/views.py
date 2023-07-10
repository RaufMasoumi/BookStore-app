from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from books.views import book_list_filtering_showing, paginate_books
from .models import Category

# Create your views here.


class CategoryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Category
    template_name = 'categories/category_list.html'
    login_url = 'account_login'
    permission_required = 'categories.category_list'

    
class CategoryBooksListView(ListView):
    template_name = 'categories/category_books_list.html'
    context_object_name = 'category_books'

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        self.category = get_object_or_404(Category, pk=pk)
        queryset = self.category.books.all()
        queryset, self.availability_on_key, self.price_on_key, self.available_on_key, self.price_less_key, \
        self.price_more_key, self.order_by = book_list_filtering_showing(queryset, self.request)
        return queryset

    def get_paginate_by(self, *args):
        paginate_by = 9
        if self.request.GET.get('showing') and self.request.GET.get('show'):
            paginate_by = paginate_books(self.request)
        return paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['fast_view_books'] = context['category_books']
        context['active_category_set'] = make_active_category_set(self.category)
        context['available_on_key'] = self.available_on_key
        context['availability_on_key'] = self.availability_on_key
        context['price_on_key'] = self.price_on_key
        context['price_less_key'] = self.price_less_key
        context['price_more_key'] = self.price_more_key
        context['order_by'] = self.order_by
        context['paginate_by'] = self.get_paginate_by()
        return context


class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Category
    fields = '__all__'
    template_name = 'categories/category_create.html'
    login_url = 'account_login'
    permission_required = 'categories.add_category'


class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Category
    fields = '__all__'
    template_name = 'categories/category_update.html'
    login_url = 'account_login'
    permission_required = 'categories.change_category'


class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Category
    template_name = 'categories/category_delete.html'
    login_url = 'account_login'
    success_url = reverse_lazy('category_list')
    permission_required = 'categories.delete_category'


def make_active_category_set(category):
    active_category_set = set()
    while category:
        active_category_set.add(category)
        category = category.parent
    return active_category_set

