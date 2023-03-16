"""foodgram URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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


urlpatterns = [
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
