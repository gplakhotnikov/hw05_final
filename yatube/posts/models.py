from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Введите название группы',
        help_text='Название группы')
    slug = models.SlugField(
        unique=True,
        verbose_name='Введите slug группы',
        help_text='Slug группы')
    description = models.TextField(
        verbose_name='Введите описание группы',
        help_text='Описание группы'
    )

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Введите текст',
        help_text='Текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Введите автора публикации',
        help_text='Автор публикации')
    group = models.ForeignKey(
        Group(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Выберите группу',
        help_text='Группа поста')
    image = models.ImageField(
        'Изображение',
        blank=True,
        upload_to='posts/',
        help_text='Изображение для записи'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def __str__(self):
        return self.text[:15]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post(),
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост, к которому относятся комментарии',
        help_text='Укажите пост, к которому относятся комментарии')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор публикации',
        help_text='Укажите автора публикации')

    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь, который подписывается',
        help_text='Тот пользователь, который решает подписаться на другого')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Пользователь, на которого подписываются',
        help_text='Тот пользователь, на которого решают подписаться')

    def __str__(self):
        return(f"Пользователь {self.user} фолловит пользователя {self.author}")
