from django import forms
from .models import Post


# Form class creaton using model
class PostForm (forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']

