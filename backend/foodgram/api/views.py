# from djoser.views import UserViewSet
# from rest_framework.decorators import action
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.permissions import (
#     AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
# )
# from rest_framework.response import Response
# from rest_framework.status import (HTTP_200_OK,
#                                    HTTP_400_BAD_REQUEST)
# from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

# from api.pagination import CustomPagination
# from api.permissions import IsOwnerOrReadOnly
# from api.serializers import (RecipeListSerializer,
#                              RecipeCreateUpdateSerializer,
#                              TagSerializer,
#                              UserSerializer,
#                              IngredientSerializer)
# from recipes.models import Recipe, Tag, Ingredient
# from users.models import User


# # class CustomPagination(PageNumberPagination):
# #     """Не забываем про паджинатор

# #     Причем кастомный, т.к. там ожидается параметра limit."""
# #     page_size_query_param = 'limit'


# class CustomUserViewSet(UserViewSet):
#     """Api для работы с пользователями.

#     Там все, что нам нужно. CRUD + action me и прочее. См. исходники.
#     """
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     pagination_class = CustomPagination
#     permission_classes = (IsAuthenticatedOrReadOnly,)
#     http_method_names = ('get', 'post', 'path', 'delete', 'patch')
#     lookup_field = 'username'
#     # @action(detail=False,
#     #         methods=['GET'],   
#     #         permission_classes=(IsAuthenticated,))
#     # def me(self, request):
#     #     if request.method == 'GET':
#     #         serializer = UserSerializer(request.user)
#     #         return Response(serializer.data, status=HTTP_200_OK)

#     #     serializer = UserSerializer(request.user,
#     #                                   data=request.data,
#     #                                   partial=True)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save()
#     #     return Response(serializer.data, status=HTTP_200_OK)



# class RecipesViewSet(ModelViewSet):
#     queryset = Recipe.objects.all()
#     http_method_names = ['get', 'post', 'patch', ]
#     permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
#     pagination_class = CustomPagination

#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user)

#     def get_serializer_class(self):
#         if self.action in ('create', 'update', 'partial_update'):
#             return RecipeCreateUpdateSerializer

#         return RecipeListSerializer

#     def get_queryset(self):
#         qs = Recipe.objects.add_user_annotations(self.request.user.pk)

#         # Фильтры из GET-параметров запроса, например.
#         author = self.request.query_params.get('author', None)
#         if author:
#             qs = qs.filter(author=author)

#         return qs


# class TagViewSet(ReadOnlyModelViewSet):
#     serializer_class = TagSerializer
#     queryset = Tag.objects.all()
#     pagination_class = None

# class IngredientViewSet(ReadOnlyModelViewSet):
#     serializer_class = IngredientSerializer
#     queryset = Ingredient.objects.all()
#     pagination_class = None


from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes.models import (
    Ingredient, Tag, Recipe, Favorite, ShoppingCart,
    IngredientInRecipe,
)
from users.models import User, Subscription
from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer, CustomUserSerializer, CreateRecipeSerializer,
    AddFavoritesSerializer, SubscriptionSerializer
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет работы с обьектами класса Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    # lookup_field = 'slug'


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с обьектами класса Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)

class CustomUserViewSet(UserViewSet):
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
        """Список авторов, на которых подписан пользователь."""
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
        """Подписка на автора."""
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




# class CustomUserViewSet(UserViewSet):
#     """Вьюсет для работы с обьектами класса User и подписки на авторов."""

#     queryset = User.objects.all()
#     serializer_class = CustomUserSerializer
#     permission_classes = (IsAuthenticatedOrReadOnly,)
#     pagination_class = LimitOffsetPagination

#     @action(
#         detail=False,
#         methods=('get',),
#         permission_classes=(IsAuthenticated, ),
#         url_path='subscriptions',
#         url_name='subscriptions',
#     )
#     def subscriptions(self, request):
#         """Метод для создания страницы подписок"""

#         queryset = User.objects.filter(follow__user=self.request.user)
#         if queryset:
#             pages = self.paginate_queryset(queryset)
#             serializer = FollowSerializer(pages, many=True,
#                                           context={'request': request})
#             return self.get_paginated_response(serializer.data)
#         return Response('Вы ни на кого не подписаны.',
#                         status=status.HTTP_400_BAD_REQUEST)

#     @action(
#         detail=True,
#         methods=('post', 'delete'),
#         permission_classes=(IsAuthenticated,),
#         url_path='subscribe',
#         url_name='subscribe',
#     )
#     def subscribe(self, request, id):
#         """Метод для управления подписками """

#         user = request.user
#         author = get_object_or_404(User, id=id)
#         change_subscription_status = Follow.objects.filter(
#             user=user.id, author=author.id
#         )
#         if request.method == 'POST':
#             if user == author:
#                 return Response('Вы пытаетесь подписаться на себя!!',
#                                 status=status.HTTP_400_BAD_REQUEST)
#             if change_subscription_status.exists():
#                 return Response(f'Вы теперь подписаны на {author}',
#                                 status=status.HTTP_400_BAD_REQUEST)
#             subscribe = Follow.objects.create(
#                 user=user,
#                 author=author
#             )
#             subscribe.save()
#             return Response(f'Вы подписались на {author}',
#                             status=status.HTTP_201_CREATED)
#         if change_subscription_status.exists():
#             change_subscription_status.delete()
#             return Response(f'Вы отписались от {author}',
#                             status=status.HTTP_204_NO_CONTENT)
#         return Response(f'Вы не подписаны на {author}',
#                         status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=False,
    #         methods=['GET', 'PATCH'],   
    #         permission_classes=(IsAuthenticated,))
    # def me(self, request):
    #     if request.method == 'GET':
    #         serializer = CustomUserSerializer(request.user)
    #         return Response(serializer.data, status=status.HTTP_200_OK)

    #     serializer = CustomUserSerializer(request.user,
    #                                   data=request.data,
    #                                   partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeViewSet(ModelViewSet):
    """ViewSet для обработки запросов, связанных с рецептами."""

    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Метод для вызова определенного сериализатора. """

        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        elif self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer

    def get_serializer_context(self):
        """Метод для передачи контекста. """

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
                    {'errors': f'Повторно - \"{recipe.name}\" добавить нельзя,'
                               f'он уже есть в избранном у пользователя'},
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
                           f'которого нет в списке покупок '},
                status=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def ingredients_to_txt(ingredients):
        """Метод для объединения ингредиентов в список для загрузки"""

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