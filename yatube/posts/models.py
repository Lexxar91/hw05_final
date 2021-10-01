from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text=(
            'Группа в которой можно'
            'опубликовать пост'
        )
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Сылочка',
        help_text='Кусок урла'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание группы'
    )

    def __str__(self):
        return str(self.slug)


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст для публикации'
    )
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
        help_text='Комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
        help_text='Автор'
    )
    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Поле для комментария'
                            )

    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        help_text='Дата публикации'
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        help_text='Пользователь'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор постов',
        help_text='Автор'
    )

    class Meta:
        verbose_name = 'Подписки'
        models.UniqueConstraint(
            fields=['user', 'aurhor'],
            name='unique_follow'
        )

    def __str__(self):
        return (f'{self.user.username} подписывается на автора '
                f'{self.author.username}')
