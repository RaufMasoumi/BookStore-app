from django import forms
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
