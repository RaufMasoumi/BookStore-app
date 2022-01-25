from django import forms
from .models import Review, ReviewReply


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('review',)


class ReviewReplyForm(forms.ModelForm):
    class Meta:
        model = ReviewReply
        fields = ('reply',)
