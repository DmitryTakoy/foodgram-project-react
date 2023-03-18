from django.urls import path, include
from rest_framework import routers
from .views import (RecipeViewSet,
                    IngredientViewSet,
                    TagViewSet,
                    FavoriteRecipeView,
                    add_recipe_to_shopping_cart,
                    SubscribedToView)
from .pdfgen import download_shopping_cart_t
from django.urls import path, include
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView,
                                            TokenVerifyView)
from .views import (MyProfileView,
                    UserProfileView,
                    UserListView,
                    SetPasswordView,
                    SubscriptionView,
                    SubscribersView,
                    NewSubscriptionView,
                    ObtainAuthTokenEmail,
                    LogoutView)


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
    path('api-auth/',
         include('rest_framework.urls',
                 namespace='rest_framework')),
    path('token/',
         TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/',
         TokenRefreshView.as_view(),
         name='token_refresh'),
    path('token/verify/',
         TokenVerifyView.as_view(),
         name='token_verify'),
    path('users/<int:id>/',
         UserProfileView.as_view(),
         name='user_profile'),
    path('users/me/',
         MyProfileView.as_view(),
         name='my_profile'),
    path('api/users/',
         UserListView.as_view(),
         name='user_list'),
    path('users/',
         UserListView.as_view(),
         name='user_listt'),
    path('users/set_password/',
         SetPasswordView.as_view(),
         name='set_password'),
    path('subscriptions/<int:user_id>/',
         SubscriptionView.as_view(),
         name='subscription-detail'),
    path('subscriptions/<int:user_id>/followers/',
         SubscribersView.as_view(),
         name='subscription-follower-list'),
    path('users/<int:user_id>/subscribe/',
         NewSubscriptionView.as_view(),
         name='follow'),
    path('auth/token/login/',
         ObtainAuthTokenEmail.as_view(),
         name='login'),
    path('auth/token/logout/',
         LogoutView.as_view(),
         name='api_token_logout'),
]
