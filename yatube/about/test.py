from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_urls_about(self):
        """Проверка для любого пользователя, статус и доступность шаблона."""

        test_urls = [
            ('/about/skill/', HTTPStatus.OK, 'about/skill.html'),
            ('/about/author/', HTTPStatus.OK, 'about/author.html'),
            ('/about/tech/', HTTPStatus.OK, 'about/tech.html'),
        ]

        for url, status, template in test_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status)
            self.assertTemplateUsed(response, template)
