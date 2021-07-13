from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author(self):
        """Тестирование доступности страницы об авторе"""
        response = self.guest_client.get("/about/author/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech(self):
        """Тестирование доступности страницы о технологиях"""
        response = self.guest_client.get("/about/tech/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_use_correct_template(self):
        """Тестирование вызываемых шаблонов при обращении к view-классам"""
        templates_pages_names = {
            "about/author.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech"),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
