from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Batman')

    def setUp(self):
        super().setUp()
        self.guest_client = Client()
        self.guest_client.force_login(self.user)

    def test_urls_code(self):
        """Проверка для анонимного пользователя, статус и доступа шаблона."""
        test_urls_not_found = [
            ('/auth/signup/', HTTPStatus.OK, 'users/signup.html'),
            ('/auth/login/', HTTPStatus.OK, 'users/login.html'),
            ('/auth/logout/', HTTPStatus.OK, 'users/logged_out.html'),
            (
                '/auth/password_reset/',
                HTTPStatus.OK,
                'users/password_reset_form.html',
            ),
            (
                '/auth/reset/<uidb64>/<token>/',
                HTTPStatus.OK,
                'users/password_reset_confirm.html',
            ),
            (
                '/auth/reset/done/',
                HTTPStatus.OK,
                'users/password_reset_complete.html',
            ),
            (
                '/auth/password_reset/done/',
                HTTPStatus.OK,
                'users/password_reset_done.html',
            ),
            (
                '/auth/password_change/',
                HTTPStatus.OK,
                'users/login.html',
            ),  # происходит редирект на - залогинься
            (
                '/auth/password_change/done/',
                HTTPStatus.OK,
                'users/login.html',
            ),  # происходит редирект на - залогинься
        ]

        for url, status, template in test_urls_not_found:
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, status)
            self.assertTemplateUsed(response, template)

    def test_urls_guest_client(self):
        """
        Проверка для авторизованного пользователя,
        статус и доступа шаблона
        """
        test_urls_not_found = [
            ('/auth/signup/', HTTPStatus.OK, 'users/signup.html'),
            ('/auth/login/', HTTPStatus.OK, 'users/login.html'),
            (
                '/auth/password_reset/',
                HTTPStatus.OK,
                'users/password_reset_form.html',
            ),
            (
                '/auth/reset/<uidb64>/<token>/',
                HTTPStatus.OK,
                'users/password_reset_confirm.html',
            ),
            (
                '/auth/reset/done/',
                HTTPStatus.OK,
                'users/password_reset_complete.html',
            ),
            (
                '/auth/password_reset/done/',
                HTTPStatus.OK,
                'users/password_reset_done.html',
            ),
            (
                '/auth/password_change/',
                HTTPStatus.OK,
                'users/password_change_form.html',
            ),
            (
                '/auth/password_change/done/',
                HTTPStatus.OK,
                'users/password_change_done.html',
            ),
            (
                '/auth/logout/',
                HTTPStatus.OK,
                'users/logged_out.html',
            ),  # cтавить в конец, иначе разлогинивает
        ]
        for url, status, template in test_urls_not_found:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, status)
            self.assertTemplateUsed(response, template)
