from django import forms
from .models import Review, ReviewReply


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('book', 'review')
        widgets = {'book': forms.HiddenInput}


class ReviewReplyForm(forms.ModelForm):
    class Meta:
        model = ReviewReply
        fields = ('reply',)
