from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'image', 'group',)
        labels = {
            'text': 'Текст сообщения',
            'group': 'Выберите группу',
            'image': 'Выберите изображение',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        lables = {'text': 'Ваш комментарий'}
        widgets = {'text': forms.Textarea(attrs={'cols': 80, 'rows': 3})}
