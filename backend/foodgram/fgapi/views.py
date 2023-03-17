from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Ingredient,
    Recipe,
    Tag,
    FavoriteRecipe,
    ShoppingList
)
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    SubscribedUserSerializer,
    TagSerializer,
    PostRecipeSerializer,
)
from users.models import User
from .filters import IngredientFilter
from .paginators import CustomPagination


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ('tags__slug', 'author')
    search_fields = ('title', 'ingredients__name')
    pagination_class = PageNumberPagination
    ordering = ('id', )

    def get_queryset(self):
        queryset = super().get_queryset()
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags)
        is_favorite = self.request.query_params.get('is_favorited', None)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart', None)
        if is_favorite == '1':
            queryset = queryset.filter(favoriterecipe__user=self.request.user)
        if is_in_shopping_cart is not None:
            queryset = queryset.filter(shopping_lists__user=self.request.user)
        queryset = queryset.distinct()
        return queryset

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeSerializer
        print("POSTRECIPESERIALIZERWASUSED")
        return PostRecipeSerializer

    def perform_create(self, serializer):
        # The request user is set as author automatically.
        serializer.save(author=self.request.user)


class IngredientViewSet(viewsets.ModelViewSet):
    """Manage ingredients in the database"""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_fields = {'name': ['exact', 'icontains', 'istartswith'], }
    filterset_class = IngredientFilter
    search_fields = ('name',)
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('name', None)
        if search_query:
            queryset = queryset.filter(name__istartswith=search_query)
        return queryset


class TagViewSet(viewsets.ModelViewSet):
    """Manage tags in the database"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'slug')
    pagination_class = None


class FavoriteRecipeView(APIView):
    def post(self, request, id):
        recipe = Recipe.objects.filter(id=id).first()

        if not recipe:
            return Response(
                {"detail": "Рецепт не найден"},
                status=status.HTTP_404_NOT_FOUND)

        if FavoriteRecipe.objects.filter(
                user=request.user, recipe=recipe).exists():
            return Response(
                {"detail": "Рецепт уже в списке избранных"},
                status=status.HTTP_400_BAD_REQUEST)

        favorite_recipe = FavoriteRecipe(user=request.user, recipe=recipe)
        favorite_recipe.save()

        return Response(
            {"detail": "Рецепт успешно добавлен в список избранных"},
            status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = generics.get_object_or_404(Recipe, id=id)
        try:
            favorite_recipe = FavoriteRecipe.objects.get(
                user=request.user, recipe=recipe)
            favorite_recipe.delete()
            return Response(
                {"detail": "Рецепт удален"},
                status=status.HTTP_204_NO_CONTENT)
        except FavoriteRecipe.DoesNotExist:
            return Response(
                {"detail": "Записи не существует"},
                status=status.HTTP_404_NOT_FOUND)


@api_view(['POST', 'DELETE'])
def add_recipe_to_shopping_cart(request, id):
    try:
        recipe = Recipe.objects.get(pk=id)
    except Recipe.DoesNotExist:
        return Response(
            {"error": f"Recipe with id={id} does not exist"},
            status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        user = request.user
        shopping_list, created = ShoppingList.objects.get_or_create(user=user)
        if recipe in shopping_list.recipes.all():
            return Response(
                {"error": "Recipe is already in the shopping cart"},
                status=status.HTTP_400_BAD_REQUEST)
        shopping_list.recipes.add(recipe)
        return Response(
            {"success": f"Recipe '{recipe.name}' added to the shopping cart"},
            status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        shopping_list = request.user.shopping_list
        if recipe in shopping_list.recipes.all():
            shopping_list.recipes.remove(recipe)
            shopping_list.save()

            return Response(
                {"success": f"'{recipe.name}' deleted from the shopping cart"},
                status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'error': 'Recipe is not in the shopping cart.'},
            status=status.HTTP_400_BAD_REQUEST)

# came from users


class SubscribedToView(APIView, LimitOffsetPagination):
    serializer_class = SubscribedUserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get(self, request):
        subscribed_users = request.user.subscriptions.values_list(
            'subscribed_to__id',
            flat=True)
        users = User.objects.filter(id__in=subscribed_users)

        page = self.paginate_queryset(users, request)
        if page is not None:
            serializer = SubscribedUserSerializer(
                page,
                many=True,
                context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = SubscribedUserSerializer(
            users, many=True, context={'request': request})
        return Response(serializer.data)
