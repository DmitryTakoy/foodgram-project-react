from django.contrib import admin
from django import forms
from .models import Tag, Ingredient, Recipe, IngredientAmount, FavoriteRecipe, ShoppingList


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

class RecipeForm(forms.ModelForm):
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Ингредиенты'
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['ingredients'].initial = self.instance.ingredients.values_list('pk', flat=True)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        if instance.pk:
            instance.ingredients.set(self.cleaned_data['ingredients'])
            self.save_m2m()
        return instance


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
            self.form.base_fields['ingredients'].initial = [1,]
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        # Assign the user creating the recipe to the recipe object
        obj.author = request.user
        obj.save()

admin.site.unregister(Recipe)
admin.site.register(Recipe, RecipeAdmin)