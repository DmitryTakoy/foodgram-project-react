from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.utils.translation import gettext as _
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenObtainPairSerializer
from rest_framework.authtoken.serializers import AuthTokenSerializer
from .models import Subscription, User
from django.db.models import Q


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(max_length=150, required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(max_length=150, required=True, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

class UserLoginSerializer(serializers.Serializer):
    model = User
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')
    
    def get_is_subscribed(self, obj):
        current_user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            current_user = request.user
            return Subscription.objects.filter(subscriber=current_user, subscribed_to=obj).exists()
        return False

    
class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    subscribed_to = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = Subscription
        fields = ('subscriber', 'subscribed_to',)

# Рабочая версия бещ is_subscribed
class CustUserSerializer(serializers.ModelSerializer):
    subscribers = serializers.SerializerMethodField()
    subscribed_to = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'subscribers', 'subscribed_to',)

    def get_subscribers(self, obj):
        subscribers = Subscription.objects.filter(subscribed_to=obj)
        return [subscription.subscriber.username for subscription in subscribers]

    def get_subscribed_to(self, obj):
        following = Subscription.objects.filter(subscriber=obj)
        return [subscription.subscribed_to.username for subscription in following]


## prod serialize to get token

class EmailTokenObtainSerializer(TokenObtainSerializer):
    username_field = User.EMAIL_FIELD

class EmailAuthTokenSerializer(AuthTokenSerializer):
    username = User.email

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def to_representation(self, instance):
        return {
            'access': str(instance.access_token),
        }
    
## chatgpt
class AuthTokenEmailSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                email=email,
                password=password,
            )
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs
    
# getting proper type of answer on sub-s