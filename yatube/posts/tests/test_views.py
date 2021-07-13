from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    AUTH_USER_NAME = "TestUser"
    PAGE_TEXT = "Тестовый текст"
    PAGE_GROUP = "Тестовая группа"
    GROUP_SLUG = "test-group"
    GROUP_DESCRIPTION = "Описание группы"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=cls.AUTH_USER_NAME)
        cls.group = Group.objects.create(
            title=cls.PAGE_GROUP,
            slug=cls.GROUP_SLUG,
            description=cls.GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=cls.PAGE_TEXT, author=cls.user, group=cls.group
        )

    def setUp(self):
        self.guest_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        """Тестирование вызываемых шаблонов при обращении к view-классам"""
        templates_pages_names = {
            "index.html": reverse("index"),
            "posts/new_post.html": reverse("new_post"),
            "posts/group.html": (
                reverse("group_posts", kwargs={"slug": "test-group"})
            ),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_in_index_page(self):
        """Тестирование содержания context в главной страницы"""
        response = self.authorized_client.get(reverse("index"))
        context_post = {
            self.PAGE_TEXT: response.context["page"][0].text,
            self.AUTH_USER_NAME: response.context["page"][0].author.username,
            self.PAGE_GROUP: response.context["page"][0].group.title,
        }
        for expected, value in context_post.items():
            with self.subTest(value=value):
                self.assertEqual(
                    value,
                    expected,
                    "Данные переданные в context" "не соответствуют записям",
                )

    def test_group_page_shows_correct_context(self):
        """Тестирование содержания context в страницы группы"""
        response = self.authorized_client.get(
            reverse("group_posts", kwargs={"slug": "test-group"})
        )

        context_post = {
            self.PAGE_TEXT: response.context["page"][0].text,
            self.AUTH_USER_NAME: response.context["page"][0].author.username,
            self.PAGE_GROUP: response.context["page"][0].group.title,
            self.GROUP_SLUG: response.context["page"][0].group.slug,
            self.GROUP_DESCRIPTION: response.context["page"][
                0
            ].group.description,
        }

        for expected, value in context_post.items():
            with self.subTest(value=value, expected=expected):
                self.assertEqual(
                    value,
                    expected,
                    "Данные переданные в context" "не соответствуют записям",
                )

    def test_new_post_exist(self):
        """Тестирование формы редактирования поста"""

        form_data = {
            "text": "Новый текст",
        }

        for group_id in (self.group.id, None):
            with self.subTest(group_id=group_id):
                posts_count = Post.objects.count()
                if group_id:
                    form_data["group_id"] = group_id

        response = self.authorized_client.post(
            reverse(
                "new_post",
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse("index"))
        Post.objects.filter(
            text="Новый текст", group_id=group_id, author=self.post.author
        ).exists()

    def test_post_edit_shows_correct_context(self):
        """Тестирование содержания context в страницы редактирования поста"""
        response = self.authorized_client.post(
            reverse(
                "post_edit", kwargs={"username": "TestUser", "post_id": "1"}
            )
        )

        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value, expected=expected):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_shows_correct_context(self):
        """Тестирование содержания context в страницы профиля"""

        response = self.authorized_client.get(
            reverse("profile", kwargs={"username": "TestUser"})
        )

        context_post = {
            self.PAGE_TEXT: response.context["page"][0].text,
            self.AUTH_USER_NAME: response.context["page"][0].author.username,
        }
        for expected, value in context_post.items():
            with self.subTest(value=value, expected=expected):
                self.assertEqual(
                    value,
                    expected,
                    "Данные переданные в context" "не соответствуют записям",
                )

    def test_post_id_shows_correct_context(self):
        """Тестирование содержания context в страницы отдельного поста"""
        response = self.authorized_client.get(
            reverse("post", kwargs={"username": "TestUser", "post_id": "1"})
        )

        context_post = {
            self.PAGE_TEXT: response.context["post"].text,
            self.AUTH_USER_NAME: response.context["post"].author.username,
        }
        for expected, value in context_post.items():
            with self.subTest(value=value, expected=expected):
                self.assertEqual(
                    value,
                    expected,
                    "Данные переданные в context" "не соответствуют записям",
                )

    def test_post_edit_exist(self):
        """Тестирование формы редактирования поста"""

        form_data = {
            "text": "Новый текст",
            "group": PostPagesTests.group.id,
        }

        response = self.authorized_client.post(
            reverse(
                "post_edit",
                args={PostPagesTests.post.author, PostPagesTests.post.id},
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                "post",
                args={PostPagesTests.post.author, PostPagesTests.post.id},
            ),
        )
        Post.objects.filter(
            text="Новый текст", group=self.group, author=self.post.author
        ).exists()


class PaginatorViewsTest(TestCase):
    """Тестирование паджинатора"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="TestUser")
        posts = (Post(text=f"Пост №{i}", author=cls.user) for i in range(13))
        Post.objects.bulk_create(posts, 13)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(len(response.context.get("page").object_list), 10)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse("index") + "?page=2")
        self.assertEqual(len(response.context.get("page").object_list), 3)
