from django.http import Http404
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from collectify.permissions import IsOwnerOrReadOnly
from .authentication import JWTAuthenticationExcludeSafeMethods
from .serializers import CollectifyTokenObtainPairSerializer, UserSerializer, \
    CollectifyTokenObtainPairSerializerUsingIdToken, UserProfileSerializer
from .models import User


class ObtainTokenPairWithAddedClaimsView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)  # default requires authentication, hence we must use `AllowAny`
    serializer_class = CollectifyTokenObtainPairSerializer


class ObtainTokenPairUsingIdToken(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)  # default requires authentication, hence we must use `AllowAny`
    serializer_class = CollectifyTokenObtainPairSerializerUsingIdToken


class UserCreate(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        try:
            if serializer.is_valid():
                user = serializer.save()
                if user:
                    json = serializer.data
                    return Response(json, status=status.HTTP_201_CREATED)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except APIException as err:
            return Response({"detail": err.detail}, status=status.HTTP_400_BAD_REQUEST)


class UserInfo(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    authentication_classes = [JWTAuthenticationExcludeSafeMethods]
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'username'


class UserInfoFromToken(APIView):
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
