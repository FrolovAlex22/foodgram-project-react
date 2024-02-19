from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AddFavoritesSerializer,
    CreateRecipeSerializer,
    CustomUserSerializer,
    IngredientSerializer,
    RecipeSerializer,
    SubscriptionSerializer,
    TagSerializer
)
from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, ShoppingCart, Tag
)
from users.models import User, Subscription


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет работы с обьектами класса Tag"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с обьектами класса Ingredient"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы с обьектами класса User"""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    @action(
        detail=False,
        methods=("get",),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Список подписок пользователь."""
        user = self.request.user
        queryset = user.follower.all()
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("post", "delete"),
    )
    def subscribe(self, request, id=None):
        """Подписка на автора"""
        user = self.request.user
        author = get_object_or_404(User, pk=id)

        if user == author:
            return Response(
                {"errors": "Нельзя подписаться или отписаться от себя!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if self.request.method == "POST":
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {"errors": "Подписка уже оформлена!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            queryset = Subscription.objects.create(author=author, user=user)
            serializer = SubscriptionSerializer(
                queryset, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            if not Subscription.objects.filter(
                user=user, author=author
            ).exists():
                return Response(
                    {"errors": "Вы уже отписаны!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subscription = get_object_or_404(
                Subscription, user=user, author=author
            )
            subscription.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False,
            methods=['GET', 'PATCH'],
            url_path='me',
            url_name='me',
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        if request.method == 'GET':
            serializer = CustomUserSerializer(
                request.user,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = CustomUserSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeViewSet(ModelViewSet):
    """Вьюсет для работы с обьектами класса Recipe"""

    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Метод для вызова определенного сериализатора """

        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        elif self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer

    def get_serializer_context(self):
        """Метод для передачи контекста """

        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, pk):
        """Метод для управления избранными подписками """

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': f'Рецепт - \"{recipe.name}\" нельзя добавить,'
                               f'он уже есть в избранном у пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = AddFavoritesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            obj = Favorite.objects.filter(user=user, recipe=recipe)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': f'В избранном нет рецепта \"{recipe.name}\"'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        """Метод для управления списком покупок"""

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': f'Повторно - \"{recipe.name}\" добавить нельзя,'
                               f'он уже есть в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = AddFavoritesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            obj = ShoppingCart.objects.filter(user=user, recipe__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': f'Нельзя удалить рецепт - \"{recipe.name}\", '
                           f'его нет в списке покупок. '},
                status=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def ingredients_to_txt(ingredients):
        """Метод для состовления списка ингредиентов для загрузки"""

        shopping_list = ''
        for ingredient in ingredients:
            shopping_list += (
                f"{ingredient['ingredient__name']}  - "
                f"{ingredient['sum']}"
                f"({ingredient['ingredient__measurement_unit']})\n"
            )
        return shopping_list

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """Метод для загрузки ингредиентов и их количества
         для выбранных рецептов"""

        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(sum=Sum('amount'))
        shopping_list = self.ingredients_to_txt(ingredients)
        return HttpResponse(shopping_list, content_type='text/plain')
