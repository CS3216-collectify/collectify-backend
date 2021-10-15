from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import ObtainTokenPairWithAddedClaimsView, UserCreate, ObtainTokenPairUsingIdToken, UserInfo, \
    UserInfoFromToken

urlpatterns = [
    path('token/obtain/', ObtainTokenPairWithAddedClaimsView.as_view(), name='token_create'),
    path('token/obtain/social/', ObtainTokenPairUsingIdToken.as_view(), name='token_create_social'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('user/create/', UserCreate.as_view(), name="create_user"),
    path('user/<username>/', UserInfo.as_view(), name="user_profile"),
    path('user/', UserInfoFromToken.as_view(), name="user_profile_from_token"),
]
