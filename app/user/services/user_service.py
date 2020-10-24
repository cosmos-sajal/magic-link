from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token


class UserService():
    def does_user_exist(self, **kwargs):
        try:
            get_user_model().objects.get(**kwargs)

            return True
        except ObjectDoesNotExist:
            return False
    
    def get_user(self, **kwargs):
        try:
            return get_user_model().objects.get(**kwargs)
        except ObjectDoesNotExist:
            return None
    
    def create_user(self, **validated_data):
        """
        Creates the user in core_user table
        """

        return get_user_model().objects.create_user(**validated_data)


class TokenService():
    def __init__(self, email=None, **kwargs):
        self.email = email
        self.user_service = UserService()
        self.token = kwargs.pop('token', None)
    
    def get_token(self):
        user = self.user_service.get_user(email=self.email)
        
        try:
            token = Token.objects.get(user=user)

            return token.key
        except ObjectDoesNotExist:
            token = Token.objects.create(user=user)

            return token.key

    def delete_token(self):
        if self.token is not None:
            Token.objects.filter(key=self.token).delete()
