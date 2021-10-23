from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import SAFE_METHODS
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTAuthenticationExcludeSafeMethods(JWTAuthentication):
    def authenticate(self, request):
        if request.method in SAFE_METHODS:
            return None

        return super().authenticate(request=request)


class JWTAuthenticationWithoutErrorForSafeMethods(JWTAuthentication):
    def authenticate(self, request):
        if request.method in SAFE_METHODS:
            try:
                return super().authenticate(request=request)
            except AuthenticationFailed:
                return None

        return super().authenticate(request=request)
