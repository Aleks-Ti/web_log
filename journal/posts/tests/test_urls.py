from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Batman')

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
        )
        cls.authorized_client_author_posts = (
            Client()
        )  # Автор поста, авторизованный
        cls.authorized_client_author_posts.force_login(cls.user)

        cls.hasnoname = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()  # Авторизованный, не автор
        cls.authorized_client.force_login(cls.hasnoname)

        cls.urls = {
            'index': (reverse('posts:index')),
            'group': (
                reverse('posts:group_list', kwargs={'slug': cls.group.slug})
            ),
            'profile': (
                reverse(
                    'posts:profile', kwargs={'username': cls.user.username},
                )
            ),
            'post_detail': (
                reverse('posts:post_detail', kwargs={'post_id': cls.post.pk})
            ),
            'post_create': (reverse('posts:post_create')),
            'post_edit': (
                reverse('posts:post_edit', kwargs={'post_id': cls.post.pk})
            ),
            'add_comment': (
                reverse('posts:add_comment', kwargs={'post_id': cls.post.pk})
            ),
            'follow_index': (reverse('posts:follow_index')),
            'profile_follow': (
                reverse(
                    'posts:profile_follow',
                    kwargs={'username': cls.user.username},
                )
            ),
            'profile_unfollow': (
                reverse(
                    'posts:profile_unfollow',
                    kwargs={'username': cls.user.username},
                )
            ),
            'not_found': '/unexisting_page/',
        }

    def setUp(self) -> None:
        super().setUp()
        cache.clear()

    def test_http_statuses(self) -> None:
        """
        Проверка пользователя - он же автор поста,
        статус доступа к страницам проекта.
        """
        test_status_code_url = [
            (self.urls.get('index'), HTTPStatus.OK, self.client),
            (self.urls.get('group'), HTTPStatus.OK, self.client),
            (self.urls.get('profile'), HTTPStatus.OK, self.client),
            (self.urls.get('post_detail'), HTTPStatus.OK, self.client),
            (self.urls.get('post_create'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('post_create'),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (self.urls.get('post_edit'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('post_edit'),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (
                self.urls.get('post_edit'),
                HTTPStatus.OK,
                self.authorized_client_author_posts,
            ),
            (self.urls.get('add_comment'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('add_comment'),
                HTTPStatus.FOUND,
                self.authorized_client,
            ),
            (
                self.urls.get('add_comment'),
                HTTPStatus.FOUND,
                self.authorized_client_author_posts,
            ),
            (self.urls.get('follow_index'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('follow_index'),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (
                self.urls.get('follow_index'),
                HTTPStatus.OK,
                self.authorized_client_author_posts,
            ),
            (self.urls.get('profile_follow'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('profile_follow'),
                HTTPStatus.FOUND,
                self.authorized_client,
            ),
            (
                self.urls.get('profile_follow'),
                HTTPStatus.FOUND,
                self.authorized_client_author_posts,
            ),
            (self.urls.get('profile_unfollow'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('profile_unfollow'),
                HTTPStatus.FOUND,
                self.authorized_client,
            ),
            (
                self.urls.get('profile_unfollow'),
                HTTPStatus.NOT_FOUND,
                self.authorized_client_author_posts,
            ),
            (self.urls.get('not_found'), HTTPStatus.NOT_FOUND, self.client),
        ]

        for url, status, client in test_status_code_url:
            response = client.get(url)
            self.assertEqual(response.status_code, status)

    def test_templates(self) -> None:
        """
        Проверка правильности вызова шаблона к вызваемому url.
        """
        templates = [
            (self.urls.get('index'), 'posts/index.html', self.client),
            (self.urls.get('group'), 'posts/group_list.html', self.client),
            (self.urls.get('profile'), 'posts/profile.html', self.client),
            (
                self.urls.get('post_detail'),
                'posts/post_detail.html',
                self.client,
            ),
            (
                self.urls.get('post_create'),
                'posts/create_post.html',
                self.authorized_client,
            ),
            (
                self.urls.get('post_edit'),
                'posts/create_post.html',
                self.authorized_client,
            ),
            (
                self.urls.get('post_edit'),
                'posts/create_post.html',
                self.authorized_client_author_posts,
            ),
            (
                self.urls.get('follow_index'),
                'posts/follow.html',
                self.authorized_client,
            ),
            (
                self.urls.get('follow_index'),
                'posts/follow.html',
                self.authorized_client_author_posts,
            ),
        ]

        for reverse_name, template, client in templates:
            with self.subTest(reverse_name=reverse_name):
                response = client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_redirects(self) -> None:
        """
        Проверка правильности вызова шаблона к вызваемому url.
        """
        templates = [
            (self.urls.get('post_create'), 'users/login.html', self.client),
            (self.urls.get('post_edit'), 'users/login.html', self.client),
            (
                self.urls.get('post_edit'),
                'posts/create_post.html',
                self.authorized_client,
            ),
            (
                self.urls.get('post_edit'),
                'posts/create_post.html',
                self.authorized_client_author_posts,
            ),
            (self.urls.get('add_comment'), 'users/login.html', self.client),
            (
                self.urls.get('add_comment'),
                'posts/post_detail.html',
                self.authorized_client,
            ),
            (
                self.urls.get('add_comment'),
                'posts/post_detail.html',
                self.authorized_client_author_posts,
            ),
            (self.urls.get('follow_index'), 'users/login.html', self.client),
            (self.urls.get('profile_follow'), 'users/login.html', self.client),
            (
                self.urls.get('profile_follow'),
                'posts/profile.html',
                self.authorized_client,
            ),
            (
                self.urls.get('profile_follow'),
                'posts/profile.html',
                self.authorized_client_author_posts,
            ),
            (
                self.urls.get('profile_unfollow'),
                'users/login.html',
                self.client,
            ),
            (
                self.urls.get('profile_unfollow'),
                'posts/profile.html',
                self.authorized_client,
            ),
            (
                self.urls.get('profile_unfollow'),
                'core/404.html',
                self.authorized_client_author_posts,
            ),
            (self.urls.get('not_found'), 'core/404.html', self.client),
        ]

        for reverse_name, template, client in templates:
            with self.subTest(reverse_name=reverse_name):
                response = client.get(reverse_name, follow=True)
                self.assertTemplateUsed(response, template)
