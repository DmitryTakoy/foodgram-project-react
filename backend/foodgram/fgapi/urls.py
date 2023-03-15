from django.urls import path, include
from rest_framework import routers
from .views import RecipeViewSet, IngredientViewSet, TagViewSet, FavoriteRecipeView
from .views import add_recipe_to_shopping_cart, SubscribedToView
from .pdfgen import download_shopping_cart_t


router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)

app_name = 'fgapi'
print("urls.py is being processed...")
urlpatterns = [
    path('api/recipes/download_shopping_cart/', download_shopping_cart_t, name='download_shopping_cart'),
    path('api/', include(router.urls)),
    path('api/recipes/<int:id>/favorite/', FavoriteRecipeView.as_view(), name='favorite_recipe'),
    path('api/recipes/<int:id>/shopping_cart/', add_recipe_to_shopping_cart, name='add_recipe_to_shopping_cart'),
    #path('api/what/', SubscribedToView.as_view())
    path('api/users/subscriptions/', SubscribedToView.as_view(), name='subscription-list'),
]