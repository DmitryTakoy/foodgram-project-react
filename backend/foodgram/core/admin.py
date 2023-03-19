# Register your models here.
from django.contrib import admin
from .models import User, Subscription
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib import admin
from django.utils.html import format_html
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
    prepopulated_fields = {'slug': ('name',)}


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
    list_display = (
        'name',
        'author',
        'cooking_time',
        'favorite_count',
        'display_image',
        'display_ingredients')
    
    def display_ingredients(self, obj):
        ingredients = obj.ingredients.all()
        ingredients_names = ', '.join([ingredient.name for ingredient in ingredients[:3]])
        if len(ingredients) > 3:
            ingredients_names += ', ...'
        return ingredients_names
    display_ingredients.short_description = 'Ingredients'

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return 'No Image'
    display_image.short_description = 'Image Preview'

    def favorite_count(self, obj): 
        return obj.favoriterecipe_set.count() 
    favorite_count.short_description = 'Favorite Count' 

    def get_form(self, request, obj=None, **kwargs): 
        return super().get_form(request, obj, **kwargs) 

    def save_model(self, request, obj, form, change): 
        obj.author = request.user 
        obj.save() 


admin.site.unregister(Recipe)
admin.site.register(Recipe, RecipeAdmin)
