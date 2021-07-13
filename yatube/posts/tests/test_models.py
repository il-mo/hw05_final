from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTests(TestCase):
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
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_name(self):
        """Тестирование отображение __str__ в модели Post"""
        post = PostModelTests.post
        expected_post_contain = post.text[:15]
        self.assertEqual(expected_post_contain, str(post))

    def test_group_title(self):
        """Тестирование отображение __str__ в модели Group"""
        group = PostModelTests.group
        expected_group_title = group.title
        self.assertEqual(expected_group_title, str(group))
