from django.db import models

# Create your models here.
from django import forms
from django.db import models
from django.contrib import admin
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission

from django.db.models import Q
from django.utils.translation import gettext as _

# Came from users

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
USER_ROLE_CHOICES = [
    ('user', USER),
    ('moderator', MODERATOR),
    ('admin', ADMIN)
]


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    EMAIL_FIELD = 'email'
    email = models.EmailField(
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    role = models.CharField(
        max_length=255,
        choices=USER_ROLE_CHOICES,
        default=USER,
        verbose_name='Роль'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )
    groups = models.ManyToManyField(
        Group,
        related_name='custom_users',
        blank=True,
        verbose_name=_('Группы'),
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_users',
        blank=True,
        verbose_name=_('Разрешения пользователя'),
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_admin(self):
        return self.role == ADMIN


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions')
    subscribed_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscribers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'subscribed_to')
        verbose_name = 'Подписки'


from django.contrib.auth.backends import ModelBackend
# не могу переместить этот импорт и ничего с ним сделать.
# суммарно 5-6 часов потратил чтобы
# убрать или переместить, что только не перeпробовал -
# все ломает приложение с ошибкой
# ""django.core.exceptions.ImproperlyConfigured:
# AUTH_USER_MODEL refers to model 'core.User' that has not been installed""


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username))
        except User.DoesNotExist:
            User().set_password(password)
        else:
            if user.check_password(
                    password) and self.user_can_authenticate(user):
                return user

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None


# Came from fgapi
class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    color = models.CharField(max_length=7, verbose_name='Цветовой HEX-код')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100, verbose_name='Название'
        )
    measurement_unit = models.CharField(
        max_length=50, verbose_name='Единица измерения'
        )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество',
        blank=True,
        null=True
        )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
    name = models.CharField(
        max_length=200, verbose_name='Название')
    image = models.ImageField(
        upload_to='images/', verbose_name='Изображение')
    text = models.TextField(
        verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        Tag, verbose_name='Теги')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (мин)')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts',
        verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент')
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество')

    class Meta:
        verbose_name = 'Количество ингридиента'
        verbose_name_plural = 'Количество ингридиентов'

    def __str__(self):
        return (f"{self.ingredient.name} - "
                f"{self.amount} {self.ingredient.measurement_unit}")


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        unique_together = ('user', 'recipe')


class ShoppingList(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь')
    recipes = models.ManyToManyField(
        Recipe,
        blank=True,
        related_name='shopping_lists',
        verbose_name='Рецепты')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f"Список покупок пользователя {self.user.username}"


class RecipeForm(forms.ModelForm):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        through_fields=('recipe', 'ingredient'),
        related_name='recipes',
        verbose_name='Ингредиенты'
    )

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeAdmin(admin.ModelAdmin):
    form = RecipeForm


admin.site.register(Recipe, RecipeAdmin)
