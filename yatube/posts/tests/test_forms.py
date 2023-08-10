import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post
from posts.tests.common import image

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = User.objects.create_user(username='Batman')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        cache.clear()

    def test_create_post(self):
        """Тестирование создания поста и его занесение в БД."""
        group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        create_post = {
            'text': 'Супер информативный текст для вставки в форму',
            'group': group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=create_post,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        post = Post.objects.get(text=create_post['text'])
        self.assertEqual(post.text, create_post['text'])
        self.assertEqual(post.group.pk, create_post['group'])

    def test_edit_post(self):
        """
        Тестирование редактирования поста и занесение
        в БД c новыми данными.
        """
        group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=group,
        )
        data = {
            'text': 'Тестовый  пост отредактировался!',
            'group': group.pk,
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(post.id,)),
            data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        post_edit = Post.objects.get(id=post.pk)
        self.assertEqual(post_edit.text, data['text'])
        self.assertEqual(post_edit.group.pk, data['group'])

    def test_not_create_post_anonim(self):
        """
        Доступ анонимного пользователя к страницe
        создания поста.
        """
        response = self.client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_not_edit_post_anonim(self):
        """
        Доступ анонимного пользователя к страницe редактирования поста.
        """
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        response = self.client.get(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_edit_post_authorized_client_not_author_post(self):
        """
        Доступ авторизованного пользователя к редактированию
        поста другого автора.
        """
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )

        self.user = User.objects.create_user(username='grenka')
        self.authorized_other_client = Client()
        self.authorized_other_client.force_login(self.user)

        response = self.authorized_other_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_picture_post(self):
        """Тест на добавление поста с кратинкой через форму пользователем."""
        create_post = {
            'author': self.user,
            'text': 'Тест поста с картинкой',
            'image': image(),
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=create_post,
            follow=True,
        )

        post = Post.objects.filter(
            author=self.user,
            text='Тест поста с картинкой',
            image='posts/test.png',
        )

        self.assertEqual(post[0].text, create_post['text'])
        self.assertEqual(post[0].author, create_post['author'])
        self.assertEqual(post[0].image, 'posts/test.png')


class FollowCreateTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Batman')

    def test_authorized_client_subscribe(self):
        """
        Тестирование возможности авторизованного пользователя подписаться
        на автора постов.
        """
        self.haruf = User.objects.create_user(username='Харуф')
        self.unique_client = Client()
        self.unique_client.force_login(self.haruf)

        self.unique_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user.username},
            ),
        )

        follow = Follow.objects.filter(user=self.haruf, author=self.user)
        self.assertTrue(follow.exists())

    def test_authorized_client_unsubscribe(self):
        """
        Тестирование возможности авторизованного пользователя отписаться
        от автора постов.
        """
        self.haruf = User.objects.create_user(username='Харуф')
        self.unique_client = Client()
        self.unique_client.force_login(self.haruf)

        self.unique_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user.username},
            ),
        )

        follow = Follow.objects.filter(user=self.haruf, author=self.user)
        self.assertFalse(follow.exists())

    def test_authorized_client_sign_up_for_yourself(self):
        """
        Тестирование возможности авторизованного пользователя
        подписаться на себя.
        """
        self.haruf = User.objects.create_user(username='Харуф')
        self.unique_client = Client()
        self.unique_client.force_login(self.haruf)

        response = [
            (
                reverse(
                    'posts:profile_follow',
                    kwargs={'username': self.haruf.username},
                ),
                HTTPStatus.FOUND,
            ),
        ]

        for url, status in response:
            response = self.unique_client.get(url)
            self.assertEqual(response.status_code, status)

        follow = Follow.objects.filter(user=self.haruf, author=self.haruf)
        self.assertFalse(follow.exists())

    def test_anonim_subscribe_and_unsubscribe(self):
        """
        Тестирование возможности анонима подписаться и отписаться
        от автора постов.

        Анонимный клиент должен быть переадресован на страницу авторизации.
        """

        response = [
            (
                reverse(
                    'posts:profile_follow',
                    kwargs={'username': self.user.username},
                ),
                HTTPStatus.OK,
                'users/login.html',
            ),
            (
                reverse(
                    'posts:profile_unfollow',
                    kwargs={'username': self.user.username},
                ),
                HTTPStatus.OK,
                'users/login.html',
            ),
        ]

        for url, status, template in response:
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, status)
            self.assertTemplateUsed(response, template)
