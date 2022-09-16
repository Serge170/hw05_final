from django.contrib.auth import get_user_model
from django.db import models
from core.models import CreatedModel

User = get_user_model()

LENGTH_TEXT = 15
"""Количество символов"""


class Group (models.Model):
    """ Страница со списком постов."""
    title = models.CharField(max_length=200, verbose_name='заголовок',)
    slug = models.SlugField(max_length=200, unique=True,)
    description = models.TextField(verbose_name='описание группы',)

    def __str__(self):
        return self.title


class Post(CreatedModel, models.Model):
    """ Главная страница."""
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Напишите содержимое поста',
        max_length=5000, )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор поста',
        related_name='posts')
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Здесь можно выбрать группу',
        related_name='posts')

    image = models.ImageField(
        verbose_name='Картинка',
        help_text='Здесь можно добавить картинку',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        """Переопределение Meta."""
        ordering = ['-created']

    def __str__(self):
        return self.text[:LENGTH_TEXT]


class Comment(models.Model):
    """Класс для комментирования записей."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='запись'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        'Текст',
        help_text='Текст нового комментария'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created',)

    def __str__(self):
        return self.text[:LENGTH_TEXT]


class Follow(models.Model):
    """Параметры добавления новых подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        default_related_name = "following"
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_list'),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='author'
            )
        ]

    def __str__(self):
        return f"Подписчик: '{self.user}' на автора: '{self.author}'"