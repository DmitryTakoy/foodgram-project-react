import base64
from django.core.files.base import ContentFile
from rest_framework import serializers
from core.models import Recipe, Ingredient, Tag, IngredientAmount
from core.models import User, Subscription
from djoser.serializers import UserSerializer
from django.utils.translation import gettext as _
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.authtoken.serializers import AuthTokenSerializer
from core.models import Subscription, User
from django.db.models import Q


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user objects"""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """
        Get subscription status of the user
        """
        current_user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user') and \
                request.user.is_authenticated:
            current_user = request.user
            return Subscription.objects.filter(
                subscriber=current_user,
                subscribed_to=obj
            ).exists()
        return False


class Base64ImageField(serializers.ImageField):
    """
    A custom image field serializer handle image data encoded as base64 string.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngAmounToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='ingredient.id')
    name = serializers.CharField(
        source='ingredient.name', required=False)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', required=False)
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientAmountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(
        read_only=True)
    ingredients = IngAmounToRecipeSerializer(
        many=True, read_only=True, source='ingredient_amounts')
    tags = TagSerializer(
        many=True, read_only=False)
    image = Base64ImageField(
        required=False)
    is_favorited = serializers.SerializerMethodField(
        default=False)
    is_in_shopping_cart = serializers.SerializerMethodField(
        default=False)

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time']

    def to_internal_value(self, data):
        if data.get('image') and isinstance(data['image'], str) \
                and data['image'].startswith('data:image'):
            data['image'] = Base64ImageField().to_internal_value(data['image'])
        return super().to_internal_value(data)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favoriterecipe_set.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.shopping_lists.filter(user=request.user).exists()
        return False


class PostRecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientAmountSerializer(
        many=True)
    image = Base64ImageField(
        required=False)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'ingredients', 'text',
                  'tags', 'image', 'cooking_time']

    def create(self, validated_data):
        ingredients_data = self.initial_data['ingredients']
        tags_data = self.initial_data['tags']
        validated_data.pop('tags')
        validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount'])
            recipe.save()
            recipe.ingredients.add(ingredient)
        for tag_data in tags_data:
            try:
                tag = Tag.objects.get(id=tag_data)
                recipe.tags.add(tag)
            except Tag.DoesNotExist:
                raise serializers.ValidationError(
                    f"Tag with slug {tag_data} does not exist")
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get(
            'name', instance.name)
        instance.text = validated_data.get(
            'text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.image = validated_data.get(
            'image', instance.image)

        # Update the tags for the recipe
        tags_data = validated_data.pop('tags')
        instance.tags.clear()
        for tag_data in tags_data:
            try:
                tag = Tag.objects.get(id=tag_data.id)
                instance.tags.add(tag)
            except Tag.DoesNotExist:
                raise serializers.ValidationError(
                    f"Tag with ID {tag_data.id} does not exist")

        # Update the ingredients for the recipe
        ingredients_data = validated_data.pop('ingredients')
        ingredient_amounts = instance.ingredient_amounts.all()
        for ingredient_amount in ingredient_amounts:
            ingredient_amount.delete()

        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            IngredientAmount.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=ingredient_data['amount'])

        instance.save()
        return instance


class RecipeForSubsSerializer(RecipeSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

# came from users


class SubscribedUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count']

    def get_is_subscribed(self, obj):
        current_user = None
        request = self.context.get('request')
        if request and hasattr(
                request, 'user') and request.user.is_authenticated:
            current_user = request.user
            return Subscription.objects.filter(
                subscriber=current_user,
                subscribed_to=obj).exists()
        return False

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)[:3]
        return RecipeForSubsSerializer(
            recipes,
            many=True,
            read_only=True,
            context=self.context).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


# came from users


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user
    """

    email = serializers.EmailField(required=True)
    username = serializers.CharField(
        max_length=150,
        required=True
    )
    first_name = serializers.CharField(
        max_length=150,
        required=True
    )
    last_name = serializers.CharField(
        max_length=150,
        required=True
    )
    password = serializers.CharField(
        max_length=150,
        required=True,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""

    model = User
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscription objects"""

    subscriber = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    subscribed_to = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscription
        fields = ('subscriber', 'subscribed_to',)


class CustUserSerializer(serializers.ModelSerializer):
    """Serializer for user objects with subscribers and subscribed_to fields"""

    subscribers = serializers.SerializerMethodField()
    subscribed_to = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'subscribers', 'subscribed_to',
        )

    def get_subscribers(self, obj):
        """
        Get the list of usernames of subscribers of the user
        """
        subscribers = Subscription.objects.filter(subscribed_to=obj)
        return [
            subscription.subscriber.username
            for subscription in subscribers
        ]

    def get_subscribed_to(self, obj):
        """
        Get the list of usernames of users subscribed by the user
        """
        following = Subscription.objects.filter(subscriber=obj)
        return [
            subscription.subscribed_to.username
            for subscription in following
        ]


class EmailTokenObtainSerializer(TokenObtainSerializer):
    """TokenObtainSerializer that uses email as the username field"""

    username_field = User.EMAIL_FIELD


class EmailAuthTokenSerializer(AuthTokenSerializer):
    """AuthTokenSerializer that uses email as the username field"""

    username = User.email


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """TokenObtainPairSerializer that returns only the access token"""

    def to_representation(self, instance):
        return {'access': str(instance.access_token)}


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
