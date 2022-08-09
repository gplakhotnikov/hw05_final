from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Введите название группы')
    slug = models.SlugField(
        unique=True,
        verbose_name='Slug группы',
        help_text='Введите slug группы')
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Введите описание группы')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации',
        help_text='Введите автора публикации')
    group = models.ForeignKey(
        Group(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа поста',
        help_text='Выберите группу поста')
    image = models.ImageField(
        verbose_name='Изображение',
        blank=True,
        upload_to='posts/',
        help_text='Изображение для записи'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

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
        verbose_name='Пост, к которому относятся комментарий',
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

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


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

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('user', 'author'),
                                    name='unique_pair'),)
        verbose_name = 'Модель Follow (user фолловит author)'
        verbose_name_plural = 'Модели Follow'

    def __str__(self):
        return(f'Пользователь {self.user} фолловит пользователя {self.author}')
