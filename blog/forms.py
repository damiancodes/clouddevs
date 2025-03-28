from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    """Form for blog comments"""
    class Meta:
        model = Comment
        fields = ['name', 'email', 'website', 'content']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Your Website (optional)'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Comment', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['website'].required = False


class SearchForm(forms.Form):
    """Form for blog search"""
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search the blog...',
        })
    )