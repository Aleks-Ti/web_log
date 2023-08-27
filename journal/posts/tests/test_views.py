import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Batman')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded,
        )

    def setUp(self):
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        dubl_key_url = 'posts/create_post.html'
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'},
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk},
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            ),
            dubl_key_url: reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk},
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_group_0, self.post.group)
        self.assertEqual(post_image_0, self.post.image)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_group_0, self.post.group)
        self.assertEqual(post_image_0, self.post.image)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        self.user = User.objects.create_user(username='Superman')
        self.post = Post.objects.create(
            author=self.user,
            text='Геройский пост!',
            group=self.group,
            image=self.uploaded,
        )

        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}),
        )
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_group_0, self.post.group)
        self.assertEqual(post_image_0, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        first_object = response.context['post']
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_group_0, self.post.group)
        self.assertEqual(post_image_0, self.post.image)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильными полями."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_create_post_show_correct_context(self):
        """
        Шаблон редактирования create_post сформирован
        с правильными полями и данными.
        """
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        self.assertEqual(
            response.context['form'].initial['text'],
            self.post.text,
        )

    def test_not_post_in_group(self):
        """Проверка входит ли в группу пост, который ей не предназначен."""
        self.group_1 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test_1-slug',
            description='Текст - тестовая группа для того '
            'что туда ни один пост не входит',
        )
        response = self.client.get(f'/group/{self.group_1.slug}/')
        self.assertNotContains(response, self.post)

    def test_not_post_in_profile(self):
        """
        Проверка входит ли в profile пользователя,
        пост другого автора
        """
        self.user_1 = User.objects.create_user(username='Горыныч')
        self.post_1 = Post.objects.create(
            author=self.user_1,
            text='Я существую лишь миг... '
            'Destroying test database for alias "default"',
            group=self.group,
        )
        response = self.client.get(f'/profile/{self.post.author}/')
        self.assertNotContains(response, self.post_1)

    def test_create_post_show_in_index(self):
        """Проверка, появляется ли пост на главной странице index."""
        response = self.client.get(reverse('posts:index'))
        self.assertContains(response, self.post)

    def test_comment_anonim_client(self):
        """Тест возможности комментировать пост анонимным пользователем."""
        create_comment = {
            'text': 'Коммент анонимного пользователя',
        }

        self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=create_comment,
            follow=True,
        )

        self.assertFalse(
            Comment.objects.filter(
                text='Коммент анонимного пользователя',
            ).exists(),
        )

    def test_comment_authorized_client(self):
        """
        Тест возможности авторизованного пользователя комментировать пост.
        """
        create_comment = {
            'text': 'Коммент авторизованного пользователя',
        }

        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=create_comment,
            follow=True,
        )

        comment = Comment.objects.filter(post=self.post).select_related(
            'author',
        )
        self.assertTrue(
            Comment.objects.filter(
                text=comment[0].text,
            ).exists(),
        )

    def test_comment_view_in_post_detail(self):
        """Комментарий появляется на странице поста."""
        create_comment = {
            'text': 'Успешно отправленный коммент '
            'авторизованного пользователя',
        }

        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=create_comment,
            follow=True,
        )

        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        post_comment = response.context['post']
        comment = post_comment.comments.first().text
        self.assertEqual(comment, create_comment['text'])

    def test_cache_index_page_posts(self):
        """Тест кеширования постов в index."""
        post = Post.objects.create(
            author=self.user,
            text='Уникальный тест кэша!',
        )
        response = self.authorized_client.get(reverse('posts:index'))
        count_all_post = len(response.content)
        post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        count_after_removal = len(response.content)
        self.assertEqual(count_after_removal, count_all_post)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, count_all_post)

    def test_subscription_posts_in_follow_index(self):
        """
        Новая запись пользователя появляется в ленте тех,
        кто на него подписан.
        """
        self.client = User.objects.create_user(username='Харуф')
        self.unique_client = Client()
        self.unique_client.force_login(self.client)

        self.unique_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user.username},
            ),
        )

        response_follow_index = self.unique_client.get(
            reverse('posts:follow_index'),
        )
        response_profile_author = self.unique_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            ),
        )

        first_object = response_follow_index.context['page_obj'][0]
        second_object = response_profile_author.context['page_obj'][0]
        self.assertEqual(first_object, second_object)

    def test_unsubscribe_posts_in_not_post_follow_index(self):
        """
        Новая запись пользователя не появляется в ленте тех,
        кто на него не подписан.
        """
        self.client = User.objects.create_user(username='Харуф')
        self.unique_client = Client()
        self.unique_client.force_login(self.client)

        self.unique_client.post(
            'posts:profile_unfollow',
            kwargs={'username': self.user.username},
        )

        response_follow_index = self.unique_client.get(
            reverse('posts:follow_index'),
        )
        response_profile_author = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            ),
        )

        first_object = len(response_follow_index.context['page_obj'])
        second_object = len(response_profile_author.context['page_obj'])

        self.assertEqual(first_object, 0)
        self.assertEqual(second_object, 1)
        self.assertNotEqual(first_object, second_object)

    def test_authorized_client_subscribe(self):
        """
        Тестирование возможности авторизованного пользователя подписаться
        на автора постов.
        """
        self.haruf = User.objects.create_user(username='Харуф')
        self.unique_client = Client()
        self.unique_client.force_login(self.haruf)

        self.unique_client.post(
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

        self.unique_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user.username},
            ),
        )

        follow = Follow.objects.filter(user=self.haruf, author=self.user)
        self.assertFalse(follow.exists())


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username='Batman')
        cls.group = Group.objects.create(
            title='Тестовая группа для пагинатора',
            slug='test-slug',
            description='Тестовое описание',
        )

        for _ in range(0, 15):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group,
            )

    def setUp(self) -> None:
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        cache.clear()

    def test_first_page_contains_index(self):
        """Проверка первой страницы паджинатор шаблона index."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_index(self):
        """Проверка второй страницы паджинатор шаблона index."""
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2',
        )
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_first_page_contains_group_list(self):
        """Проверка первой страницы паджинатор шаблона group_list."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_group_list(self):
        """Проверка второй страницы паджинатор шаблона group_list."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            + '?page=2',
        )
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_first_page_contains_profile(self):
        """Проверка первой страницы паджинатор шаблона profile."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}),
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_profile(self):
        """Проверка второй страницы паджинатор шаблона profile."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
            + '?page=2',
        )
        self.assertEqual(len(response.context['page_obj']), 5)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class DeleteViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username='Yorik')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self) -> None:
        super().setUp()
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_delete_post(self):
        """Тест удаления поста."""
        post_index = self.authorized_client.get(
            reverse('posts:index'),
        )
        post_base = post_index.context['page_obj'][0]
        self.assertEqual(post_base, self.post)

        self.authorized_client.post(
            reverse('posts:post_delete', kwargs={'post_id': self.post.id}),
        )

        post = Post.objects.filter(id=self.post.id).exists()
        self.assertFalse(post)
