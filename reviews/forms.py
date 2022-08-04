from django import forms
from .models import Review, ReviewReply


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('author', 'name', 'email', 'review', 'rating', 'book')
        widgets = {'book': forms.HiddenInput}


class ReviewUserForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('book', 'review', 'rating')
        widgets = {'book': forms.HiddenInput}


class ReviewReplyForm(forms.ModelForm):
    class Meta:
        model = ReviewReply
        fields = ('reply',)