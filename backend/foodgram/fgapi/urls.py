from django.urls import path, include
from rest_framework import routers
from .views import (RecipeViewSet,
                    IngredientViewSet,
                    TagViewSet,
                    FavoriteRecipeView,
                    add_recipe_to_shopping_cart,
                    SubscribedToView)
from .pdfgen import download_shopping_cart_t


router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)

app_name = 'fgapi'
urlpatterns = [
    path('recipes/download_shopping_cart/',
         download_shopping_cart_t,
         name='download_shopping_cart'),
    path('', include(router.urls)),
    path('recipes/<int:id>/favorite/',
         FavoriteRecipeView.as_view(),
         name='favorite_recipe'),
    path('recipes/<int:id>/shopping_cart/',
         add_recipe_to_shopping_cart,
         name='add_recipe_to_shopping_cart'),
    path('users/subscriptions/',
         SubscribedToView.as_view(),
         name='subscription-list'),
]
