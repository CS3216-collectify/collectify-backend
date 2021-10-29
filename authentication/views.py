from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status, permissions, generics, exceptions
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from stream_chat import StreamChat

from collectify.permissions import IsOwnerOrReadOnly
from .authentication import JWTAuthenticationExcludeSafeMethods
from .models import User
from .serializers import CollectifyTokenObtainPairSerializer, UserSerializer, \
    CollectifyTokenObtainPairSerializerUsingIdToken, UserProfileSerializer
from collectify.collectifysecrets import STREAM_CHAT_API_SECRET
from collectify.collectifysecrets import STREAM_CHAT_API_KEY

server_client = StreamChat(api_key=STREAM_CHAT_API_KEY, api_secret=STREAM_CHAT_API_SECRET)


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
                    server_client.update_users([{
                        "id": str(user.id),
                        "name": f"{user.first_name} {user.last_name}".strip(),
                        "username": user.username,
                        "image": user.picture_file.url
                    }])
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
            if "username" in request.data or "first_name" in request.data or "last_name" in request.data or "picture_url" in request.data:
                server_client.update_users([{
                    "id": request.user.id,
                    "name": f"{request.user.first_name} {request.user.last_name}",
                    "username": request.user.username,
                    "image": request.user.picture_file.url
                }])
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

            if "username" in request.data or "first_name" in request.data or "last_name" in request.data or "picture_url" in request.data:
                server_client.update_users([{
                    "id": str(request.user.id),
                    "name": f"{request.user.first_name} {request.user.last_name}".strip(),
                    "username": request.user.username,
                    "image": request.user.picture_file.url
                }])

            return Response(status=status.HTTP_204_NO_CONTENT)
        except IntegrityError as err:
            print(err)
            if "unique constraint \"authentication_user_username_key\"" in str(err):
                raise exceptions.ValidationError(detail={"username": ["The username has already been taken."]},
                                                 code=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        user_id = request.user.id
        request.user.delete()
        server_client.delete_user(str(user_id), mark_messages_deleted=False)
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
