from rest_framework.permissions import SAFE_METHODS
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class JWTAuthenticationExcludeSafeMethods(JWTAuthentication):
    def authenticate(self, request):
        if request.method in SAFE_METHODS:
            return None

        return super().authenticate(request=request)
