# from typing import Optional

# from django.contrib.auth import get_user_model
# from django.core.validators import MaxValueValidator, MinValueValidator
# from django.db import models
# from django.db.models import Exists, OuterRef

# User = get_user_model()

# class Ingredient(models.Model):
#     """Ингредиенты."""
#     name = models.CharField(max_length=200, verbose_name='Название')
#     measurement_unit = models.CharField(
#         max_length=200, verbose_name='Единицы измерения'
#     )

#     class Meta:
#         verbose_name = 'Ингредиент'
#         verbose_name_plural = 'Ингредиенты'

#     def __str__(self):
#         return f'{self.name} ({self.measurement_unit})'

# class RecipeQuerySet(models.QuerySet):

#     def add_user_annotations(self, user_id: Optional[int]):
#         return self.annotate(
#             is_favorite=Exists(
#                 Favorite.objects.filter(
#                     user_id=user_id, recipe__pk=OuterRef('pk')
#                 )
#             ),
#         )

# class Tag(models.Model):
#     """Тэги."""
#     name = models.CharField(
#         max_length=200, verbose_name='Название', unique=True
#     )
#     color = models.CharField(
#         max_length=200, null=True, verbose_name='Цвет', unique=True
#     )
#     slug = models.SlugField(
#         max_length=200, null=True, verbose_name='Слаг', unique=True
#     )


# class Recipe(models.Model):
#     """Рецепты."""
#     author = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='recipes',
#         verbose_name='Автор')
#     name = models.CharField(
#         max_length=200,
#         verbose_name='Название рецепта')
#     images = models.ImageField(
#         upload_to='cats/images/',
#         null=True,
#         default=None
#     )
#     text = models.TextField(verbose_name='Текст')
#     ingredients = models.ManyToManyField(
#         Ingredient,
#         through='RecipeIngredient',
#         through_fields=('recipe', 'ingredient'),
#         verbose_name='Ингредиенты'
#     )
#     tags = models.ManyToManyField(
#         Tag,
#         verbose_name='Ингредиенты'
#     )
#     time = models.PositiveBigIntegerField(
#         verbose_name="Время приготовления",
#         validators=[
#             MinValueValidator(
#                 1,
#                 "Блюдо должно готовиться больше 1 минуты"
#             )
#         ]
#     )
#     slug = models.SlugField(verbose_name='Слаг')
#     pub_date = models.DateTimeField(
#         verbose_name='Дата публикации',
#         auto_now_add=True,
#         db_index=True
#     )

#     objects = RecipeQuerySet.as_manager()

#     class Meta:
#         ordering = ('-pub_date', )
#         verbose_name = 'Рецепт'
#         verbose_name_plural = 'Рецепты'

# class RecipeIngredient(models.Model):
#     amount = models.PositiveIntegerField(
#         verbose_name='Количество'
#     )
#     ingredient = models.ForeignKey(
#         Ingredient,
#         on_delete=models.CASCADE,
#         verbose_name='Ингредиент'
#     )
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE,
#         verbose_name='Рецепт'
#     )

#     def __str__(self):
#         return f'{self.ingredient} в {self.recipe}'

#     class Meta:
#         verbose_name = 'Ингредиент в рецепте'
#         verbose_name_plural = 'Ингредиенты в рецептах'


# class Favorite(models.Model):
#     """Избранное."""
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='favorites',
#         verbose_name='Пользователь'
#     )
#     recipe = models.ForeignKey(
#         Recipe,
#         on_delete=models.CASCADE,
#         related_name='favorites',
#         verbose_name='Рецепт'
#     )

#     def __str__(self):
#         return f'Избранный {self.recipe} у {self.user}'

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('user', 'recipe'),
#                 name='unique_favorite_user_recipe'
#             )
#         ]
#         verbose_name = 'Объект избранного'
#         verbose_name_plural = 'Объекты избранного'


from django.contrib.auth import get_user_model
from django.core.validators import (MinValueValidator, RegexValidator, )
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель для описания тега"""

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название тэга')
    color = models.CharField(
        'Цвет',
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение не является цветом в формате HEX!'
            )
        ],
        default='#006400',
        help_text='Введите цвет тега. Например, #006400',
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Уникальный слаг')

    class Meta:
        """Мета-параметры модели"""

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'color', 'slug'),
                name='unique_tags',
            ),
        )

    def __str__(self):
        """Метод строкового представления модели."""

        return self.name


class Ingredient(models.Model):
    """Модель для описания ингредиента"""

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название ингредиента')

    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения')

    class Meta:
        """Мета-параметры модели"""

        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        """Метод строкового представления модели."""

        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель для описания рецепта"""

    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        verbose_name='Фотография рецепта',
        upload_to='recipes/',
        blank=True
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(1, message='Минимальное значение 1!'),
        ]
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации рецепта'
    )

    REQUIRED_FIELDS = [
        'ingredients',
        'tags',
        'image',
        'name',
        'text',
        'cooking_time'
    ]

    class Meta:
        """Мета-параметры модели"""

        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created',)

    def __str__(self):
        """Метод строкового представления модели."""

        return self.name


class IngredientInRecipe(models.Model):
    """Модель для описания количества ингредиентов в отдельных рецептах"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='in_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(1, message='Минимальное количество 1!'),
        ]
    )

    class Meta:
        """Мета-параметры модели"""

        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredients_in_the_recipe'
            )
        ]

    def __str__(self):
        """Метод строкового представления модели."""

        return f'{self.ingredient} {self.recipe}'


class TagInRecipe(models.Model):
    """Создание модели тегов рецепта."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Теги',
        help_text='Выберите теги рецепта'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт')

    class Meta:
        """Мета-параметры модели"""

        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'
        constraints = [
            models.UniqueConstraint(fields=['tag', 'recipe'],
                                    name='unique_tagrecipe')
        ]

    def __str__(self):
        """Метод строкового представления модели."""

        return f'{self.tag} {self.recipe}'


class ShoppingCart(models.Model):
    """Модель для описания формирования покупок """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт'
    )

    class Meta:
        """Мета-параметры модели"""

        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoppingcart'
            )
        ]

    def __str__(self):
        """Метод строкового представления модели."""

        return f'{self.user} {self.recipe}'


# class Follow(models.Model):
#     """ Модель для создания подписок на автора"""

#     author = models.ForeignKey(
#         User,
#         related_name='follow',
#         on_delete=models.CASCADE,
#         verbose_name='Автор рецепта',
#     )
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='follower',
#         verbose_name='Подписчик'
#     )

#     class Meta:
#         """Мета-параметры модели"""

#         verbose_name = 'Подписка'
#         verbose_name_plural = 'Подписки'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['user', 'author'], name='unique_follow'
#             )
#         ]

#     def __str__(self):
#         """Метод строкового представления модели."""

#         return f'{self.user} {self.author}'


class Favorite(models.Model):
    """Модель для создания избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        """Мета-параметры модели"""

        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]

    def __str__(self):
        """Метод строкового представления модели."""

        return f'{self.user} {self.recipe}'
