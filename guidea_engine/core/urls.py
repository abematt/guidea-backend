from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LocationViewSet, TextSnippetViewSet, AudioSnippetViewSet, TourViewSet,
    RegisterView, LoginView, LogoutView, UserProfileView, UserView
)

router = DefaultRouter()
router.register(r'locations', LocationViewSet)
router.register(r'text-snippets', TextSnippetViewSet)
router.register(r'audio-snippets', AudioSnippetViewSet)
router.register(r'tours', TourViewSet)

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
    path('auth/user/', UserView.as_view(), name='user'),
] + router.urls
