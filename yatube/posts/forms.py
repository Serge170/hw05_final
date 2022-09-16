from django import forms
from django.core.exceptions import ValidationError

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """ Форма поста."""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image', )


def clean_text(self):
    text = self.cleaned_date['text']
    if len(text) > 500:
        raise ValidationError('Длина текста больше 100 символов')
    return text


class CommentForm(forms.ModelForm):
    """ Форма комментария."""
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст',
        }
        help_texts = {
            'text': 'Текст нового комментария',
        }
