from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.http import JsonResponse

from .models import Post
#  импортируйте в код всё необходимое


class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ('text', 'author', 'pub_date')
