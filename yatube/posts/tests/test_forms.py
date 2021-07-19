import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    AUTH_USER_NAME = "TestUser"
    PAGE_TEXT = "Тестовый текст"
    PAGE_GROUP = "Тестовая группа"
    GROUP_SLUG = "test-group"
    GROUP_DESCRIPTION = "Описание группы"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(username=cls.AUTH_USER_NAME)
        cls.group = Group.objects.create(
            title=cls.PAGE_GROUP,
            slug=cls.GROUP_SLUG,
            description=cls.GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=cls.PAGE_TEXT, author=cls.user, group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_page(self):
        """Тестирование формы создания нового поста c картинкой"""
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )

        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )

        form_data = {
            "text": "Тестовый текст",
            "image": uploaded,
        }

        for group_id in (self.group.id, None):
            with self.subTest(group_id=group_id):
                posts_count = Post.objects.count()
                if group_id:
                    form_data["group_id"] = group_id

        response = self.authorized_client.post(
            reverse("new_post"), data=form_data, follow=True
        )
        self.assertRedirects(response, reverse("index"))

        self.assertTrue(
            Post.objects.filter(
                text="Тестовый текст",
                group_id=group_id,
                image="posts/small.gif",
            ).exists()
        )

        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_edit(self):
        """Тестирование формы редактирования поста"""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Новый текст",
            "group": self.group.id,
        }

        response = self.authorized_client.post(
            reverse("post_edit", args={self.post.author, self.post.id}),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response, reverse("post", args={self.post.author, self.post.id})
        )

        self.assertTrue(
            Post.objects.filter(
                text="Новый текст",
                group=self.group,
            ).exists()
        )
        self.assertEqual(Post.objects.count(), posts_count)
