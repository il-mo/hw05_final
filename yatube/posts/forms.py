from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {
            "text": "Текст сообщения",
            "group": "Выберите группу",
        }


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            "post",
            "text",
        )
