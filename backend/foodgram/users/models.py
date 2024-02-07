from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомный класс пользователя."""
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        max_length=150
    )
    last_name = models.CharField(
        max_length=150
    )
    password = models.CharField(
        max_length=150
    )
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "username", "first_name", "last_name", "password"]

    def __str__(self):
        return self.username


