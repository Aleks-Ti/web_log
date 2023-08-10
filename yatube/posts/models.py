from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField('Текст поста', help_text='Введите текст поста')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор',
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='groups',
        verbose_name='группа',
        help_text='Группа, к котрой будет относиться пост',
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[: settings.TEXT_BLOCK]


class Group(models.Model):
    title = models.CharField('название', max_length=200)
    description = models.TextField('описание')
    slug = models.SlugField('slug', max_length=50, unique=True)

    def __str__(self) -> str:
        return self.title[: settings.TEXT_BLOCK_TITLE]


class Comment(models.Model):
    text = models.TextField('Комментарий', help_text='Ваш коментарий')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор комментария',
    )
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='комментарий',
    )

    def __str__(self) -> str:
        return self.text[: settings.TEXT_BLOCK]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    def __str__(self) -> str:
        return self.author[: settings.TEXT_BLOCK_TITLE]
