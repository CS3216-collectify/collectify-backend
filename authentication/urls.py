from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import ObtainTokenPairWithAddedClaimsView, UserCreate

urlpatterns = [
    path('token/obtain/', ObtainTokenPairWithAddedClaimsView.as_view(), name='token_create'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('user/create/', UserCreate.as_view(), name="create_user"),
]