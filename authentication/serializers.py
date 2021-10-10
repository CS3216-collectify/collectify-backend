from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers, exceptions, status
from rest_framework_simplejwt.settings import api_settings

from .models import User
from google.oauth2 import id_token
from google.auth.transport import requests


class CollectifyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims:
        # token['key_name'] = user.some_key
        return token

    def validate(self, attrs):
        if 'id_token' not in attrs:
            # Use login credentials
            return super().validate(attrs)

        # Verify token
        print(attrs['id_token'])
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
            if not idinfo['email'] or not idinfo['given_name'] or not idinfo['family_name'] or not idinfo['picture']:
                raise ValueError('Requires email and profile scopes.')

            queryset = User.objects.filter(email=idinfo['email'])

            if len(queryset) > 1:
                raise ValueError('Multiple emails found.')

            if len(queryset) == 0:
                self.user = User.objects.create_user(
                    idinfo['sub'],  # use google's userid as username for now.
                    email=idinfo['email'],
                    first_name=idinfo['given_name'],
                    last_name=idinfo['family_name'],
                    picture=idinfo['picture']
                )

            if len(queryset) == 1:
                self.user = queryset[0]

            # generate access token
            refresh = self.get_token(self.user)
            data = {'refresh': str(refresh), 'access': str(refresh.access_token)}

            if api_settings.UPDATE_LAST_LOGIN:
                update_last_login(None, self.user)

            return data

        except ValueError as err:
            # Invalid token
            print(err)
            raise exceptions.AuthenticationFailed(
                self.error_messages['Invalid ID Token'],
                'Invalid_ID_Token',
            )


class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='id')
    email = serializers.EmailField(
        required=True
    )
    username = serializers.CharField()
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
