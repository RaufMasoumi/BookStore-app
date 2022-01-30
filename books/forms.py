from django import forms
from datetime import date, datetime
from .models import Book, BookImage, Review, ReviewReply


BookImageFormSet = forms.inlineformset_factory(Book, BookImage, fields='__all__')


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('book', 'review',)
        widgets = {'book': forms.HiddenInput}


class ReviewReplyForm(forms.ModelForm):
    class Meta:
        model = ReviewReply
        fields = ('reply',)


class BookSearchForm(forms.Form):
    search = forms.CharField(max_length=100)
    title = forms.BooleanField(required=False)
    author = forms.BooleanField(required=False)
    less = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='price less than:')
    more = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='price more than:')
    available = forms.BooleanField(required=False, label='only available books?')


class BookMakePublishedForm(forms.Form):
    publish = forms.BooleanField(required=False)


# is not in using
class DateSelectorWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        days = [(day, day) for day in range(1, 32)]
        months = [(month, month) for month in range(1, 13)]
        years = [(year, year) for year in range(1800, datetime.now().year + 1)]
        widgets = [
            forms.Select(attrs=attrs, choices=days),
            forms.Select(attrs=attrs, choices=months),
            forms.Select(attrs=attrs, choices=years),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if isinstance(value, date):
            return [value.day, value.month, value.year]
        elif isinstance(value, str):
            year, month, day = value.split('-')
            return [day, month, year]
        return [None, None, None]

    def value_from_datadict(self, data, files, name):
        day, month, year = super().value_from_datadict(data, files, name)
        return '{}-{}-{}'.format(year, month, day)

