from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostUrlsTests(TestCase):
    AUTH_USER_NAME = 'TestUser'
    PAGE_TEXT = 'Тестовый текст'
    PAGE_GROUP = 'Тестовая группа'
    GROUP_SLUG = 'test-group'
    GROUP_DESCRIPTION = 'Описание группы'

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

        self.user_not_author = User.objects.create_user(
            username='TestUserNotAuthor'
        )
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_not_author)

    def test_pages_url_exists_at_desired_location(self):
        """Тестирование доступности страниц"""
        pages_status = {
            HTTPStatus.OK: self.guest_client.get('/').status_code,
            HTTPStatus.OK: self.guest_client.get(
                '/group/test-group/'
            ).status_code,
            HTTPStatus.OK: self.authorized_client.get('/new/').status_code,
            HTTPStatus.OK: self.guest_client.get('/TestUser/').status_code,
            HTTPStatus.OK: self.guest_client.get('/TestUser/1/').status_code,
            HTTPStatus.FOUND: self.guest_client.get(
                '/TestUser/1/edit/'
            ).status_code,
            HTTPStatus.OK: self.authorized_client.get(
                '/TestUser/1/edit/'
            ).status_code,
            HTTPStatus.FOUND: self.authorized_client_not_author.get(
                '/TestUser/1/edit/'
            ).status_code,
            HTTPStatus.NOT_FOUND: self.guest_client.get('/14/88/').status_code,
        }
        for expected, value in pages_status.items():
            with self.subTest(value=value, expected=expected):
                self.assertEqual(
                    value, expected, 'Статус страницы не правильный'
                )

    def test_new_post_url_redirect_anonymous_on_login(self):
        """Тестирование редиректа со страницы создания поста
        при отсутвии прав доступа"""
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_post_edit_url_redirect_anonymous_on_login(self):
        """Тестирование редиректа со страницы редактирования поста
        при отсутвии прав доступа"""
        response = self.guest_client.get('/TestUser/1/edit/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/TestUser/1/edit/')

    def test_urls_uses_correct_template(self):
        """Тестирование вызываемых шаблонов"""
        templates_url_names = {
            'posts/new_post.html': '/TestUser/1/edit/',
            'posts/group.html': '/group/test-group/',
            'posts/follow.html': '/follow/',
        }

        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_edit_page_uses_correct_template(self):
        """Тестирование вызываемого шаблона создание поста"""
        response = self.authorized_client.get('/new/')
        self.assertTemplateUsed(response, 'posts/new_post.html')

    # def test_edit_page_uses_correct_template(self):
    #     """Тестирование вызываемого шаблона главной страницы"""
    #     response = self.guest_client.get('/')
    #     self.assertTemplateUsed(response, 'index.html')
