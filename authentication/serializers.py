from urllib.request import urlopen

from django.contrib.auth.models import update_last_login
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import serializers, exceptions, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class CollectifyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims:
        # token['key_name'] = user.some_key
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['id'] = self.user.id
        return data


class CollectifyTokenObtainPairSerializerUsingIdToken(serializers.Serializer):
    default_error_messages = {
        'Invalid_id_token': 'Invalid id token.'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_token'] = serializers.CharField()

    @classmethod
    def get_token(cls, user):
        token = RefreshToken.for_user(user)

        # Add custom claims:
        # token['key_name'] = user.some_key
        return token

    def validate(self, attrs):
        try:
            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(attrs['id_token'], requests.Request())
            print(idinfo)

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # Verify that the client is one of ours.
            # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
            #     raise ValueError('Could not verify audience.')

            # Get email address and search database for user
            # If none then create a new user
            if 'email' not in idinfo or 'given_name' not in idinfo or 'picture' not in idinfo:
                raise ValueError('Requires email and profile scopes.')

            queryset = User.objects.filter(email=idinfo['email'])

            if len(queryset) > 1:
                raise ValueError('Multiple emails found.')

            if len(queryset) == 0:
                img_temp = NamedTemporaryFile()
                img_temp.write(urlopen(idinfo['picture']).read())
                img_temp.flush()

                self.user = User.objects.create_user(
                    idinfo['sub'],  # use google's userid as username for now.
                    email=idinfo['email'],
                    first_name=idinfo['given_name'],
                )
                if 'family_name' in idinfo:
                    self.user.last_name = idinfo['family_name']

                self.user.picture_file.save(idinfo['sub'], File(img_temp))
                self.user.save()
                self.is_new = True

            if len(queryset) == 1:
                self.user = queryset[0]
                self.is_new = False

            # generate access token
            refresh = self.get_token(self.user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'id': self.user.id,
                'is_new': self.is_new
            }

            if api_settings.UPDATE_LAST_LOGIN:
                update_last_login(None, self.user)

            return data

        except ValueError as err:
            # Invalid token
            print(err)
            raise exceptions.AuthenticationFailed(
                self.error_messages['Invalid_id_token'],
                'Invalid_id_token',
            )


class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='id')
    email = serializers.EmailField(
        required=True
    )
    username = serializers.CharField(min_length=8)
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ('user_id', 'email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)  # as long as the fields are the same, we can just use this
        if password is not None:
            instance.set_password(password)

        try:
            instance.save()
            return instance
        except Exception as err:
            raise exceptions.APIException(detail="User already exists", code=status.HTTP_400_BAD_REQUEST)


class UserProfileSerializer(UserSerializer):
    picture_url = serializers.URLField(read_only=True, allow_null=True)
    username = serializers.CharField(min_length=8)
    description = serializers.CharField(max_length=500)

    class Meta:
        model = User
        fields = ('user_id', 'email', 'username', 'first_name', 'last_name', 'picture_url', 'description')
