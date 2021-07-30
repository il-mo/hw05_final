import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    AUTH_USER_NAME = 'TestUser'
    USER_NAME = 'TestUser2'
    PAGE_TEXT = 'Тестовый текст'
    PAGE_GROUP = 'Тестовая группа'
    GROUP_SLUG = 'test-group'
    GROUP_DESCRIPTION = 'Описание группы'
    IMAGE = 'posts/small.gif'

    @classmethod
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.upload = SimpleUploadedFile(
            name='small.gif', content=small_gif, content_type='image/gif'
        )
        cls.user = User.objects.create(username=cls.AUTH_USER_NAME)
        cls.user2 = User.objects.create(username=cls.USER_NAME)
        cls.group = Group.objects.create(
            title=cls.PAGE_GROUP,
            slug=cls.GROUP_SLUG,
            description=cls.GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=cls.PAGE_TEXT,
            author=cls.user,
            group=cls.group,
            image=cls.upload,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.authorized_client2 = Client()
        self.authorized_client.force_login(self.user2)

        cache.clear()

    def test_pages_use_correct_template(self):
        """Тестирование вызываемых шаблонов при обращении к view-классам"""
        templates_pages_names = {
            'index.html': reverse('index'),
            'posts/new_post.html': reverse('new_post'),
            'posts/group.html': (
                reverse('group_posts', kwargs={'slug': 'test-group'})
            ),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_in_index_page(self):
        """Тестирование содержания context в главной страницы"""
        response = self.guest_user.get(reverse('index'))
        context_post = {
            self.PAGE_TEXT: response.context['page'][0].text,
            self.AUTH_USER_NAME: response.context['page'][0].author.username,
            self.PAGE_GROUP: response.context['page'][0].group.title,
            self.IMAGE: response.context['page'][0].image,
        }
        for expected, value in context_post.items():
            with self.subTest(value=value):
                self.assertEqual(
                    value,
                    expected,
                    'Данные переданные в context' 'не соответствуют записям',
                )

    def test_group_page_shows_correct_context(self):
        """Тестирование содержания context в страницы группы"""
        response = self.guest_user.get(
            reverse('group_posts', kwargs={'slug': 'test-group'})
        )

        context_post = {
            self.PAGE_TEXT: response.context['page'][0].text,
            self.AUTH_USER_NAME: response.context['page'][0].author.username,
            self.PAGE_GROUP: response.context['page'][0].group.title,
            self.GROUP_SLUG: response.context['page'][0].group.slug,
            self.GROUP_DESCRIPTION: response.context['page'][
                0
            ].group.description,
            self.IMAGE: response.context['page'][0].image,
        }

        for expected, value in context_post.items():
            with self.subTest(value=value, expected=expected):
                self.assertEqual(
                    value,
                    expected,
                    'Данные переданные в context' 'не соответствуют записям',
                )

    def test_new_post_exist(self):
        """Тестирование формы редактирования поста"""

        form_data = {
            'text': 'Новый текст',
        }

        for group_id in (self.group.id, None):
            with self.subTest(group_id=group_id):
                if group_id:
                    form_data['group_id'] = group_id

            response = self.authorized_client.post(
                reverse(
                    'new_post',
                ),
                data=form_data,
                follow=True,
            )
            self.assertRedirects(response, reverse('index'))
            Post.objects.filter(
                text='Новый текст',
                group_id=group_id,
                author=self.post.author,
            ).exists()

    def test_profile_shows_correct_context(self):
        """Тестирование содержания context в страницы профиля"""

        response = self.guest_user.get(
            reverse('profile', kwargs={'username': 'TestUser'})
        )

        context_post = {
            self.PAGE_TEXT: response.context['page'][0].text,
            self.AUTH_USER_NAME: response.context['page'][0].author.username,
            self.IMAGE: response.context['page'][0].image,
        }
        for expected, value in context_post.items():
            with self.subTest(value=value, expected=expected):
                self.assertEqual(
                    value,
                    expected,
                    'Данные переданные в context' 'не соответствуют записям',
                )

    def test_post_id_shows_correct_context(self):
        """Тестирование содержания context в страницы отдельного поста"""
        response = self.guest_user.get(
            reverse('post', kwargs={'username': 'TestUser', 'post_id': '1'})
        )

        context_post = {
            self.PAGE_TEXT: response.context['post'].text,
            self.AUTH_USER_NAME: response.context['post'].author.username,
            self.IMAGE: response.context['post'].image,
        }
        for expected, value in context_post.items():
            with self.subTest(value=value, expected=expected):
                self.assertEqual(
                    value,
                    expected,
                    'Данные переданные в context' 'не соответствуют записям',
                )

    def test_post_edit_exist(self):
        """Тестирование формы редактирования поста"""

        form_data = {
            'text': 'Новый текст',
            'group': PostPagesTests.group.id,
        }

        response = self.authorized_client.post(
            reverse(
                'post_edit',
                args={PostPagesTests.post.author, PostPagesTests.post.id},
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'post',
                args={PostPagesTests.post.author, PostPagesTests.post.id},
            ),
        )
        Post.objects.filter(
            text='Новый текст', group=self.group, author=self.post.author
        ).exists()

    def test_follow_view(self):
        """Тестирование функции подписки"""
        self.authorized_client.get(
            reverse('profile_follow', kwargs={'username': 'TestUser'})
        )
        self.assertTrue(
            Follow.objects.filter(user=self.user2, author=self.user).exists()
        )

    def test_unfollow_view(self):
        """Тестирование функции отподписки"""
        Follow.objects.create(user=self.user2, author=self.user)
        self.authorized_client.get(
            reverse('profile_unfollow', kwargs={'username': 'TestUser'})
        )
        self.assertFalse(
            Follow.objects.filter(user=self.user2, author=self.user).exists()
        )


class PaginatorViewsTest(TestCase):
    """Тестирование паджинатора"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        posts = (Post(text=f'Пост №{i}', author=cls.user) for i in range(13))
        Post.objects.bulk_create(posts, 13)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)


class CacheViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        post_text = 'Тестовый текст'
        Post.objects.create(text=post_text, author=cls.user)

    def setUp(self):
        self.guest_user = Client()

    def test_index_cache(self):
        """Тестирование работы кэша главной страницы"""
        response = self.client.get(reverse('index'))
        post_text_after_cache = 'Текстовый текст2'
        Post.objects.create(text=post_text_after_cache, author=self.user)
        second_response = self.guest_user.get(reverse('index'))

        self.assertNotEqual(
            len(response.context.get('page').object_list),
            len(second_response.context.get('page').object_list),
        )
