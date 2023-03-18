# Register your models here.
from django.contrib import admin
from .models import User, Subscription
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib import admin
from .models import (Recipe, IngredientAmount,
                     Tag, Ingredient, FavoriteRecipe, ShoppingList)
from .forms import RecipeForm


# admin.site.unregister(User)
# came from users
class UserAdmin(DefaultUserAdmin):
    search_fields = ['username', 'email']


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)


# came from fgapi
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    pass


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    pass


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    form = RecipeForm
    inlines = [IngredientAmountInline]
    list_display = ('name', 'author', 'cooking_time', 'favorite_count')

    def favorite_count(self, obj):
        return obj.favoriterecipe_set.count()
    favorite_count.short_description = 'Favorite Count'

    def get_form(self, request, obj=None, **kwargs):
        # Use our custom form for the RecipeAdmin
        if obj is None:
            # In case of adding a new Recipe
            self.form.base_fields['ingredients'].initial = [1, ]
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        # Assign the user creating the recipe to the recipe object
        obj.author = request.user
        obj.save()


admin.site.unregister(Recipe)
admin.site.register(Recipe, RecipeAdmin)
