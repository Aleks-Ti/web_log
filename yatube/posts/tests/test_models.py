from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Comment, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_return_correct_str(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        self.assertEqual(self.post.text, str(self.post))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'pub_date': 'Дата публикации',
            'text': 'Текст поста',
            'author': 'автор',
            'group': 'группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).verbose_name,
                    expected,
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к котрой будет относиться пост',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).help_text,
                    expected,
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_return_correct_str(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        self.assertEqual(self.group.title, str(self.group))


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый коммент',
        )

    def test_return_correct_str(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        self.assertEqual(self.comment.text, str(self.comment))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'pub_date': 'Дата публикации',
            'text': 'Комментарий',
            'author': 'автор комментария',
            'post': 'комментарий',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Comment._meta.get_field(value).verbose_name,
                    expected,
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Ваш коментарий',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Comment._meta.get_field(value).help_text,
                    expected,
                )
