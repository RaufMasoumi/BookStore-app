from django import forms
from django.forms import Form
from django.shortcuts import get_object_or_404
from books.models import Book
from .models import UserCartBooksNumber


def validate_number(number, stock):
    if number > stock:
        raise forms.ValidationError('The book has not enough stock!')


class UserCartNumberByNumberForm(Form):
    number_pk = forms.IntegerField(min_value=0)
    quantity = forms.IntegerField(min_value=0)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('number_pk'):
            number = get_object_or_404(UserCartBooksNumber, pk=cleaned_data['number_pk'])
            stock = number.book.stock
            stock += number.number
            validate_number(cleaned_data.get('quantity'), stock)


class UserCartNumberByBookForm(Form):
    book_pk = forms.UUIDField()
    quantity = forms.IntegerField(required=False, min_value=0)

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if not quantity:
            quantity = 1
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('book_pk'):
            book = get_object_or_404(Book, pk=cleaned_data['book_pk'])
            validate_number(cleaned_data.get('quantity'), book.stock)


class UserCartBookDeleteForm(Form):
    delete_book_pk = forms.UUIDField()
