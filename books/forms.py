from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = '__all__'
        widgets = {k: forms.HiddenInput for k in [field.name for field in Review._meta.fields]
                   if k != 'review' and k != 'id'}

