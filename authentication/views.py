from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status, permissions, generics, exceptions
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from collectify.permissions import IsOwnerOrReadOnly
from .authentication import JWTAuthenticationExcludeSafeMethods
from .models import User
from .serializers import CollectifyTokenObtainPairSerializer, UserSerializer, \
    CollectifyTokenObtainPairSerializerUsingIdToken, UserProfileSerializer


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

    def update(self, request, *args, **kwargs):
        try:
            super().update(request, *args, **kwargs)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as err:
            print(err)
            raise err
        except IntegrityError as err:
            print(err)
            if "unique constraint \"authentication_user_username_key\"" in str(err):
                raise exceptions.ValidationError(detail={"username": ["The username has already been taken."]},
                                                 code=status.HTTP_400_BAD_REQUEST)


class UserInfoFromToken(APIView):
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request, format=None):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
            if getattr(request.user, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                request.user._prefetched_objects_cache = {}

            return Response(status=status.HTTP_204_NO_CONTENT)
        except IntegrityError as err:
            print(err)
            if "unique constraint \"authentication_user_username_key\"" in str(err):
                raise exceptions.ValidationError(detail={"username": ["The username has already been taken."]},
                                                 code=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserInfoSearch(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        keywords = self.request.query_params.get('keywords')
        offset = self.request.query_params.get('offset')
        limit = self.request.query_params.get('limit')

        if keywords is not None:
            queryset = User.objects.filter(
                Q(username__istartswith=keywords)
                | Q(first_name__istartswith=keywords)
                | Q(last_name__istartswith=keywords)
            )

        else:
            queryset = User.objects.all()

        if offset is not None and limit is not None:
            queryset = queryset[int(offset):int(offset) + int(limit)]

        print(queryset)
        return queryset
