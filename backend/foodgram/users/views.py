from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Subscription, User
from .serializers import (
    AuthTokenEmailSerializer,
    CustUserSerializer,
    CustomTokenObtainPairSerializer,
    EmailAuthTokenSerializer,
    SubscriptionSerializer,
    UserCreateSerializer,
    UserLoginSerializer,
    UserSerializer,
)

from users.models import User, Subscription

from rest_framework.filters import OrderingFilter, SearchFilter

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
            return Response({"detail": "Учетные данные не были предоставлены."}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the current password is correct
        if not user.check_password(current_password):
            return Response({"current_password": ["Неверный текущий пароль"]}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a new password was provided
        if not new_password:
            return Response({"new_password": ["Необходимо ввести новый пароль"]}, status=status.HTTP_400_BAD_REQUEST)
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

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    

class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def post(self, request, user_id):
        subscribed_user = request.user
        user_to_subscribe = User.objects.get(id=user_id)

        # Check if the user is already subscribed to the given user
        if Subscription.objects.filter(subscriber=subscribed_user, subscribed_to=user_to_subscribe).exists():
            return Response({'detail': 'Вы уже подписаны на этого пользователя'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the subscription
        subscription = Subscription(subscriber=subscribed_user, subscribed_to=user_to_subscribe)
        subscription.save()

        serializer = SubscriptionSerializer(subscription)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        subscribed_user = request.user
        user_to_unsubscribe = User.objects.get(id=user_id)

        # Check if the user is subscribed to the given user
        subscription = Subscription.objects.filter(subscriber=subscribed_user, subscribed_to=user_to_unsubscribe).first()
        if not subscription:
            return Response({'detail': 'Вы не подписаны на этого пользователя'}, status=status.HTTP_400_BAD_REQUEST)

        # Delete the subscription
        subscription.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)



class SubscribedToView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ('tags__slug', 'author')

    def get(self, request):
        subscribed_users = request.user.subscriptions.values_list('subscribed_to__id', flat=True)
        users = User.objects.filter(id__in=subscribed_users)

        serializer = CustUserSerializer(users, many=True)

        return Response(serializer.data)

class SubscribersView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get(self, request):
        subscribers = request.user.subscribers.values_list('subscriber__id', flat=True)
        users = User.objects.filter(id__in=subscribers)

        serializer = CustUserSerializer(users, many=True)

        return Response(serializer.data)
    
class NewSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get(self, request, user_id):
        user = request.user
        subscriptions = Subscription.objects.filter(subscriber=user)
        subscribed_to_users = User.objects.filter(subscriptions__in=subscriptions).distinct()
        serializer = CustUserSerializer(subscribed_to_users, many=True)
        return Response(serializer.data)

    def post(self, request, user_id):
        subscribed_user = request.user
        user_to_subscribe = User.objects.get(id=user_id)

        try:
            user_to_subscribe = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the user is already subscribed to the given user
        if Subscription.objects.filter(subscriber=subscribed_user, subscribed_to=user_to_subscribe).exists():
            return Response({'detail': 'User is already subscribed to this user'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the subscription
        subscription = Subscription(subscriber=subscribed_user, subscribed_to=user_to_subscribe)
        subscription.save()

        serializer = SubscriptionSerializer(subscription)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        subscribed_user = request.user
        user_to_unsubscribe = User.objects.get(id=user_id)

        # Check if the user is subscribed to the given user
        subscription = Subscription.objects.filter(subscriber=subscribed_user, subscribed_to=user_to_unsubscribe).first()
        if not subscription:
            return Response({'detail': 'User is not subscribed to this user'}, status=status.HTTP_400_BAD_REQUEST)

        # Delete the subscription
        subscription.delete()

        return Response({'detail': 'Just unsubscribed'}, status=status.HTTP_204_NO_CONTENT)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({'auth_token': response.data['access']})
    
### try token aut to log
class ObtainAuthTokenEmail(ObtainAuthToken):
    serializer_class = AuthTokenEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "auth_token": token.key,
            },
            status=status.HTTP_200_OK,
        )
