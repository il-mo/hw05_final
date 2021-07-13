from django.contrib.auth import get_user_model
from django.db import models
from pytils.translit import slugify

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name="Название группы",
        max_length=200,
        help_text="Дайте  название вашей группе",
    )
    slug = models.SlugField(
        "Адрес для страницы с группой",
        max_length=100,
        unique=True,
        blank=True,
        help_text=(
            "Используйте только латиницу, цифры, "
            "дефисы и знаки подчёркивания"
        ),
    )
    description = models.TextField(
        verbose_name="Описание",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:100]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Содержание")
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="posts",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True,
        null=True,
    )
    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ("-pub_date",)


class Comment(models.Model):
    text = models.TextField(verbose_name="Комментарий")
    created = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ("-created",)
