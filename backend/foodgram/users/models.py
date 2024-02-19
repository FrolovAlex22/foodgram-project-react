# from django.contrib.auth.models import AbstractUser
# from django.core.validators import RegexValidator
# from django.db import models


# class User(AbstractUser):
#     """Кастомный класс пользователя."""
#     email = models.EmailField(
#         verbose_name='Электронная почта',
#         max_length=254,
#         unique=True,
#     )
#     username = models.CharField(
#         max_length=150,
#         verbose_name='Имя пользователя',
#         validators=[
#             RegexValidator(
#                 regex=r'^[\w.@+-]+$',
#                 message='Имя пользователя не соответствует, '
#                         'можно использовать только буквы, '
#                         'цифры и нижнее подчеркивания.'
#             )
#         ],
#         unique=True,
#     )
#     first_name = models.CharField(
#         max_length=150,
#         verbose_name='Имя'
#     )
#     last_name = models.CharField(
#         max_length=150,
#         verbose_name='Фамилия'
#     )
#     password = models.CharField(
#         max_length=150,
#         verbose_name='Пароль'
#     )
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

#     class Meta:
#         verbose_name = 'Пользователь'
#         verbose_name_plural = 'Пользователи'
#         ordering = ('id',)
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['username', 'email'],
#                 name='unique_username_email'
#             )
#         ]

#     def __str__(self):
#         return self.username


from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


# class User(AbstractUser):
#     """Модель для пользователей созданная для приложения foodgram"""

#     email = models.EmailField(
#         verbose_name='Электронная почта',
#         unique=True
#     )
#     username = models.CharField(
#         max_length=150,
#         verbose_name='Имя пользователя',
#         unique=True,
#         db_index=True,
#         validators=[
#             RegexValidator(
#                 regex=r'^[\w.@+-]+$',
#                 message='Имя пользователя не соответствует, '
#                         'можно использовать только буквы, '
#                         'цифры и нижнее подчеркивания.'
#             )
#         ],
#     )
#     first_name = models.CharField(
#         max_length=150,
#         verbose_name='Имя'
#     )
#     last_name = models.CharField(
#         max_length=150,
#         verbose_name='Фамилия'
#     )

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

#     class Meta:
#         """Мета-параметры модели"""

#         verbose_name = 'Пользователь'
#         verbose_name_plural = 'Пользователи'
#         ordering = ('id',)

#     def __str__(self):
#         """Строковое представление модели"""

#         return self.username
class User(AbstractUser):
    """Модель пользователей."""

    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Имя пользователя не соответствует, '
                        'можно использовать только буквы, '
                        'цифры и нижнее подчеркивания.'
            )
        ],
    )
    first_name = models.CharField(
        max_length=150,
    )
    last_name = models.CharField(
        max_length=150,
    )
    password = models.CharField(
        max_length=150,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.username



class Subscription(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

        constraints = [
            models.UniqueConstraint(
                fields=["author", "user"], name="unique_subscription"
            ),
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
