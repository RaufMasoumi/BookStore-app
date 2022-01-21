from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('book', 'review')
        widgets = {'book': forms.HiddenInput}

