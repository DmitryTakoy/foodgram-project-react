from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.views import TokenObtainPairView

from core.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    ShoppingList,
    Subscription,
    Tag,
    User,
)
from .filters import IngredientFilter
from .paginators import CustomPagination
from .serializers import (
    AuthTokenEmailSerializer,
    CustUserSerializer,
    CustomTokenObtainPairSerializer,
    IngredientSerializer,
    PostRecipeSerializer,
    RecipeSerializer,
    SubscribedUserSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserLoginSerializer,
    UserSerializer,
)


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


# came from users
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]


class UserLoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        # delete the user's token
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SetPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        # Check if the user is authenticated
        if not user.is_authenticated:
            return Response({"detail": "Учетные данные не предоставлены."},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Check if the current password is correct
        if not user.check_password(current_password):
            return Response({"current_password": ["Неверный текущий пароль"]},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if a new password was provided
        if not new_password:
            return Response({"new_password": ["Введите новый пароль"]},
                            status=status.HTTP_400_BAD_REQUEST)

        # Set the new password
        user.set_password(new_password)
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'


class UserListView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
        )
        user.save()

        return Response(
            UserSerializer(user).data, status=status.HTTP_201_CREATED
            )


class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def post(self, request, user_id):
        subscribed_user = request.user
        user_to_subscribe = User.objects.get(id=user_id)

        # Check if the user is already subscribed to the given user
        if Subscription.objects.filter(
                subscriber=subscribed_user, subscribed_to=user_to_subscribe
                ).exists():
            return Response(
                {'detail': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST)

        # Create the subscription
        subscription = Subscription(
            subscriber=subscribed_user, subscribed_to=user_to_subscribe)
        subscription.save()

        serializer = SubscriptionSerializer(subscription)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        subscribed_user = request.user
        user_to_unsubscribe = User.objects.get(id=user_id)

        # Check if the user is subscribed to the given user
        subscription = Subscription.objects.filter(
            subscriber=subscribed_user, subscribed_to=user_to_unsubscribe
            ).first()
        if not subscription:
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
                )

        # Delete the subscription
        subscription.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribedToView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    )
    filterset_fields = ('tags__slug', 'author')

    def get(self, request):
        subscribed_users = request.user.subscriptions.values_list(
            'subscribed_to__id',
            flat=True,
        )
        users = User.objects.filter(id__in=subscribed_users)
        serializer = CustUserSerializer(users, many=True)
        return Response(serializer.data)


class SubscribersView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get(self, request):
        subscribers = request.user.subscribers.values_list(
            'subscriber__id',
            flat=True,
        )
        users = User.objects.filter(id__in=subscribers)
        serializer = CustUserSerializer(users, many=True)
        return Response(serializer.data)


class NewSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get(self, request, user_id):
        user = request.user
        subscriptions = Subscription.objects.filter(subscriber=user)
        subscribed_to_users = User.objects.filter(
            subscriptions__in=subscriptions,
        ).distinct()
        serializer = CustUserSerializer(subscribed_to_users, many=True)
        return Response(serializer.data)

    def post(self, request, user_id):
        subscribed_user = request.user
        user_to_subscribe = User.objects.get(id=user_id)

        try:
            user_to_subscribe = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the user is already subscribed to the given user
        if Subscription.objects.filter(
            subscriber=subscribed_user,
            subscribed_to=user_to_subscribe,
        ).exists():
            return Response(
                {'detail': 'User is already subscribed to this user'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create the subscription
        subscription = Subscription(
            subscriber=subscribed_user,
            subscribed_to=user_to_subscribe,
        )
        subscription.save()

        serializer = SubscriptionSerializer(subscription)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        subscribed_user = request.user
        user_to_unsubscribe = User.objects.get(id=user_id)

        # Check if the user is subscribed to the given user
        subscription = Subscription.objects.filter(
            subscriber=subscribed_user,
            subscribed_to=user_to_unsubscribe,
        ).first()
        if not subscription:
            return Response(
                {'detail': 'User is not subscribed to this user'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Delete the subscription
        subscription.delete()

        return Response(
            {'detail': 'Just unsubscribed'},
            status=status.HTTP_204_NO_CONTENT,
        )


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({'auth_token': response.data['access']})


class ObtainAuthTokenEmail(ObtainAuthToken):
    serializer_class = AuthTokenEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {"auth_token": token.key},
            status=status.HTTP_200_OK,
        )
