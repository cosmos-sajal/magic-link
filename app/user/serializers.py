from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password

from helpers.validators import is_valid_email, is_strong_password


class RegisterUserSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=255)
    password = serializers.CharField(required=True, max_length=255)
    confirm_password = serializers.CharField(required=True, max_length=255)
    username = serializers.CharField(required=True, max_length=255)

    def __does_user_exist(self, **param):
        """
        Checks if user exist in the system
        Returns Boolean
        """
        try:
            get_user_model().objects.get(**param)

            return True
        except ObjectDoesNotExist:
            return False

    def validate(self, attrs):
        """
        Validate the body params
        """
        email = attrs.get('email')

        errors = {}
        if not is_valid_email(email):
            errors['email'] = ["Not a valid email"]

        if self.__does_user_exist(email=email):
            errors['email'] = ["User with this email already exist"]

        if not is_strong_password(attrs.get('password')):
            errors['password'] = ["Not a strong password"]
        
        if attrs.get('password') != attrs.get('confirm_password'):
            errors['confirm_password'] = ["Passwords do not match."]
        
        if errors == {}:
            return attrs
        else:
            raise serializers.ValidationError(errors)
    
    def create(self, validated_data):
        """
        Creates the user in core_user table
        """
        validated_data.pop('confirm_password')

        return get_user_model().objects.create_user(**validated_data)


class LoginUserSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, max_length=255)
    password = serializers.CharField(required=True, max_length=255)

    def __get_user(self, **param):
        """
        Checks if user exist in the system
        Returns Boolean
        """
        try:
            return get_user_model().objects.get(**param)
        except ObjectDoesNotExist:
            return None

    def validate(self, attrs):
        """
        Validates email and password
        """

        email = attrs.get('email')
        password = attrs.get('password')

        user = self.__get_user(email=email)
        if user is None:
            raise serializers.ValidationError("User does not exist.")
        
        if not check_password(password, user.password):
            raise serializers.ValidationError("Incorrect password.")

        attrs['user'] = user

        return attrs
