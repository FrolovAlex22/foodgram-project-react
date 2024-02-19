# #!-*-coding:utf-8-*-
# import base64

# from django.conf import settings
# from django.core.files.base import ContentFile
# from django.core.validators import RegexValidator
# from rest_framework import serializers
# from rest_framework.serializers import CharField
# from rest_framework.validators import UniqueValidator

# from recipes.models import Ingredient, RecipeIngredient, Recipe, Tag
# from users.models import User


# class Base64ImageField(serializers.ImageField):
#     def to_internal_value(self, data):
#         if isinstance(data, str) and data.startswith('data:image'):
#             format, imgstr = data.split(';base64,')
#             ext = format.split('/')[-1]

#             data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

#         return super().to_internal_value(data)


# class RecipeIngredientSerializer(serializers.ModelSerializer):
#     name = serializers.StringRelatedField(
#         source='ingredient.name'
#     )
#     measurement_unit = serializers.StringRelatedField(
#         source='ingredient.measurement_unit'
#     )
#     id = serializers.PrimaryKeyRelatedField(
#         source='ingredient',
#         queryset=Ingredient.objects.all()
#     )

#     class Meta:
#         model = RecipeIngredient
#         fields = ('amount', 'name', 'measurement_unit', 'id')


# class RecipeListSerializer(serializers.ModelSerializer):
#     """Получение списка рецептов."""

#     ingredients = serializers.SerializerMethodField()
#     is_favorite = serializers.BooleanField()
#     author = serializers.SlugRelatedField(slug_field='username',
#                                           read_only=True)

#     def get_ingredients(self, obj):
#         """Возвращает отдельный сериализатор."""
#         return RecipeIngredientSerializer(
#             RecipeIngredient.objects.filter(recipe=obj).all(), many=True
#         ).data

#     class Meta:
#         model = Recipe
#         fields = ('name', 'ingredients', 'is_favorite', 'text', 'author')


# class IngredientCreateInRecipeSerializer(serializers.ModelSerializer):
#     recipe = serializers.PrimaryKeyRelatedField(read_only=True)
#     id = serializers.PrimaryKeyRelatedField(
#         source='ingredient',
#         queryset=Ingredient.objects.all()
#     )
#     amount = serializers.IntegerField(write_only=True, min_value=1)

#     class Meta:
#         model = RecipeIngredient
#         fields = ('recipe', 'id', 'amount')


# class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
#     tags = serializers.PrimaryKeyRelatedField(
#         many=True,
#         queryset=Tag.objects.all()
#     )
#     ingredients = IngredientCreateInRecipeSerializer(many=True)
#     is_favorited = serializers.SerializerMethodField()
#     is_in_shopping_cart = serializers.SerializerMethodField()
#     author = serializers.SlugRelatedField(
#         slug_field="username", read_only=True
#     )
#     image = Base64ImageField(required=False, allow_null=True)

#     def validate_ingredients(self, value):
#         if len(value) < 1:
#             raise serializers.ValidationError("Добавьте хотя бы один ингредиент.")
#         return value

#     def create(self, validated_data):
#         tags = validated_data.pop("tags")
#         ingredients = validated_data.pop('ingredients')
#         recipe = Recipe.objects.create(**validated_data)

#         create_ingredients = [
#             RecipeIngredient(
#                 recipe=recipe,
#                 ingredient=ingredient['ingredient'],
#                 amount=ingredient['amount']
#             )
#             for ingredient in ingredients
#         ]
#         RecipeIngredient.objects.bulk_create(
#             create_ingredients
#         )
#         Tag.objects.bulk_create(tags)
#         return recipe

#     def update(self, instance, validated_data):
#         ingredients = validated_data.pop('ingredients', None)
#         if ingredients is not None:
#             instance.ingredients.clear()

#             create_ingredients = [
#                 RecipeIngredient(
#                     recipe=instance,
#                     ingredient=ingredient['ingredient'],
#                     amount=ingredient['amount']
#                 )
#                 for ingredient in ingredients
#             ]
#             RecipeIngredient.objects.bulk_create(
#                 create_ingredients
#             )
#         return super().update(instance, validated_data)

#     def to_representation(self, obj):
#         """Возвращаем прдеставление в таком же виде, как и GET-запрос."""
#         self.fields.pop('ingredients')
#         representation = super().to_representation(obj)
#         representation['ingredients'] = RecipeIngredientSerializer(
#             RecipeIngredient.objects.filter(recipe=obj).all(), many=True
#         ).data
#         return representation

#     class Meta:
#         model = Recipe
#         fields = ('name', 'ingredients', 'text')


# # class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
# #     tags = TagSerializer(many=True, read_only=False)
# #     ingredients = IngredientCreateInRecipeSerializer(many=True)
# #     is_favorited = serializers.SerializerMethodField()
# #     is_in_shopping_cart = serializers.SerializerMethodField()
# #     author = serializers.SlugRelatedField(
# #         slug_field="username", read_only=True
# #     )
# #     image = Base64ImageField(required=False, allow_null=True)

# #     def validate_ingredients(self, value):
# #         if len(value) < 1:
# #             raise serializers.ValidationError(
# #                 "Добавьте хотя бы один ингредиент."
# #             )
# #         return value

# #     def create(self, validated_data):
# #         ingredients = validated_data.pop("ingredients")
# #         tags = validated_data.pop("tags")
# #         recipe = Recipe.objects.create(**validated_data)
# #         RecipeIngredient.objects.bulk_create(ingredients)
# #         Tag.objects.bulk_create(tags)

# #         return recipe


# class TagSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Tag
#         fields = "__all__"


# class IngredientSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Ingredient
#         fields = "__all__"


# class UserSerializer(serializers.ModelSerializer):
#     """Сериализатор для User."""

#     is_subscribed = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = [
#             "email",
#             "id",
#             "username",
#             "first_name",
#             "last_name",
#             "is_subscribed",
#         ]

#     # def get_is_subscribed(self, obj):
#     #     user = self.context.get("request").user

#     #     if user.is_anonymous or (user == obj):
#     #         return False

#     #     return user.subscriptions.filter(author=obj).exists()

#     # def create(self, validated_data):
#     #     user = User(
#     #         email=validated_data["email"], username=validated_data["username"]
#     #     )
#     #     user.set_password(validated_data["password"])
#     #     user.save()
#     #     return user

import base64

import webcolors
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from djoser.serializers import UserCreateSerializer
from recipes.models import (
    Tag, Ingredient, Recipe, IngredientInRecipe,
    TagInRecipe, Favorite, ShoppingCart,
)
from users.models import User, Subscription
from api.pagination import CustomPagination


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для кодирования изображения в base64."""

    def to_internal_value(self, data):
        """Метод преобразования картинки"""

        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода тэгов."""
    color = Hex2NameColor()
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        # lookup_field = 'slug'
        # extra_kwargs = {
        #     'url': {'lookup_field': 'slug'}
        # }



class IngredientSerializer(ModelSerializer):
    """Сериализатор для вывода ингредиентов."""

    class Meta:
        """Мета-параметры сериализатора"""

        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


# class CustomUserSerializer(UserCreateSerializer):
#     """Сериализатор для модели User."""

#     is_subscribed = serializers.SerializerMethodField()

#     class Meta:
#         """Мета-параметры сериализатора"""

#         model = User
#         fields = ('email', 'id', 'username', 'first_name', 'last_name',
#                   'is_subscribed')

#     def get_is_subscribed(self, obj):
#         """Метод проверки подписки"""

#         user = self.context.get('request').user
#         if user.is_anonymous or (user == obj):
#             return False
#         return Follow.objects.filter(user=user, author=obj.id).exists()


# class CustomCreateUserSerializer(CustomUserSerializer):
#     """Сериализатор для создания пользователя
#     без проверки на подписку """

#     class Meta:
#         """Мета-параметры сериализатора"""

#         model = User
#         fields = ('email', 'id', 'username', 'first_name',
#                   'last_name', 'password')
#         extra_kwargs = {'password': {'write_only': True}}



class CustomUserSerializer(UserSerializer):
    """Проверка подписки."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user_id = self.context.get("request").user.id
        user = self.context.get('request').user
        if (user.id == None) or (user.id == obj.id):
            return False
        return Subscription.objects.filter(
            author=obj.id, user=user_id
        ).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """При создании пользователя."""

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
        )


class SubscriptionSerializer(CustomUserSerializer, CustomPagination):
    """Подписка."""

    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source="author.recipes.count")
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        """Получение списка рецептов автора."""
        from api.serializers import ShortRecipeSerializer

        author_recipes = obj.author.recipes.all()

        if author_recipes:
            serializer = ShortRecipeSerializer(
                author_recipes,
                context={"request": self.context.get("request")},
                many=True,
            )
            return serializer.data

        return []

    def get_recipes_count(self, obj):
        """Количество рецептов автора."""
        return Recipe.objects.filter(author=obj.id).count()



class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        """Мета-параметры сериализатора"""

        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientInRecipeSerializer(
        source='ingredient_list', many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Мета-параметры сериализатора"""

        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time'
                  )

    def get_is_favorited(self, obj):
        """Метод проверки на добавление в избранное."""

        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Метод проверки на присутствие в корзине."""

        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецептах"""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    @staticmethod
    def validate_amount(value):
        """Метод валидации количества"""

        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 0!'
            )
        return value

    class Meta:
        """Мета-параметры сериализатора"""

        model = IngredientInRecipe
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов"""

    ingredients = CreateIngredientsInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField(use_url=True)

    class Meta:
        """Мета-параметры сериализатора"""

        model = Recipe
        fields = ('ingredients', 'tags', 'name',
                  'image', 'text', 'cooking_time')

    def to_representation(self, instance):
        """Метод представления модели"""

        serializer = RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data

    def validate_ingredients(self, data):
        """Метод валидации ингредиентов"""

        ingredients = self.initial_data.get('ingredients')

        lst_ingredient = []

        if not ingredients:
            raise serializers.ValidationError(
                    'Блюдо должно иметь хоть какой то ингредиент!'
            )

        for element in ingredients:
            ingredient_id = element['id']
            if ingredient_id in lst_ingredient:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальными!'
                )
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    'Этого ингредиента нет в списке ингредиентов!'
                )
            lst_ingredient.append(ingredient_id)
        
        return data

    def validate_tags(self, data):

        tags = self.initial_data.get('tags')  
        lst_tag = []

        if not tags:
            raise serializers.ValidationError(
                    'Для создания рецепта нужно указать tag!'
            ) 

        for tag in tags:
            if tag in lst_tag:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальными!'
                )
            lst_tag.append(tag)

        return data

    def create_ingredients(self, ingredients, recipe):
        """Метод создания ингредиента"""

        for element in ingredients:
            id = element['id']
            ingredient = Ingredient.objects.get(pk=id)
            amount = element['amount']
            IngredientInRecipe.objects.create(
                ingredient=ingredient, recipe=recipe, amount=amount
            )

    def create_tags(self, tags, recipe):
        """Метод добавления тега"""

        recipe.tags.set(tags)

    def create(self, validated_data):
        """Метод создания модели"""

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        user = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Метод обновления модели"""

        # ingredients = validated_data.get('ingredients')
        # if ingredients is None:
        #     raise serializers.ValidationError(
        #             'Вы забыли указать ингредиенты!'
        #         )
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        TagInRecipe.objects.filter(recipe=instance).delete()

        self.create_ingredients(validated_data.pop('ingredients'), instance)
        self.create_tags(validated_data.pop('tags'), instance)

        return super().update(instance, validated_data)


class AdditionalForRecipeSerializer(serializers.ModelSerializer):
    """Дополнительный сериализатор для рецептов """

    class Meta:
        """Мета-параметры сериализатора"""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


# class FollowSerializer(CustomUserSerializer):
#     """Сериализатор для модели Follow."""

#     recipes = serializers.SerializerMethodField(
#         read_only=True,
#         method_name='get_recipes')
#     recipes_count = serializers.SerializerMethodField(
#         read_only=True
#     )

#     class Meta:
#         """Мета-параметры сериализатора"""

#         model = User
#         fields = ('email', 'id', 'username', 'first_name', 'last_name',
#                   'is_subscribed', 'recipes', 'recipes_count',)

#     def get_recipes(self, obj):
#         """Метод для получения рецептов"""

#         request = self.context.get('request')
#         recipes = obj.recipes.all()
#         recipes_limit = request.query_params.get('recipes_limit')
#         if recipes_limit:
#             recipes = recipes[:int(recipes_limit)]
#         return AdditionalForRecipeSerializer(recipes, many=True).data

#     @staticmethod
#     def get_recipes_count(obj):
#         """Метод для получения количества рецептов"""

#         return obj.recipes.count()


class AddFavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления в избранное по модели Recipe."""
    image = Base64ImageField()

    class Meta:
        """Мета-параметры сериализатора"""

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')