import json

from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from helpers.cache_adapter import CacheAdapter
from user.serializers import RegisterUserSerializer, LoginUserSerializer, \
    GenerateMagicLinkSerializer
from user.services.magic_link_service import MagicLinkService

from worker.send_email import send_email


class RegisterUserView(APIView):
    """
    Creates a user in the DB
    """

    def post(self, request):
        """
        POST API -> /api/v1/user/register/
        Validates and creates a User in core_user table
        """

        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response({'response': 'User Created!'},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateMagicLinkView(APIView):
    """
    Generates magic links for the user
    and send them over the email
    """

    def post(self, request):
        """
        POST API -> /api/v1/user/magic_link/
        """

        serializer = GenerateMagicLinkSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            service = MagicLinkService()
            res = service.generate_magic_link(
                request,
                data['user'],
                data['redirect_link']
            )
            if not res['is_success']:
                return Response({
                    'error': res['error']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            send_email.delay(res['email'], res['content'])

            return Response({
                'response': 'link sent to email'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RedirectMagicLinkView(APIView):
    """
    Redirect the user to the redirect link
    corresponding to the magic link token key
    """

    def __get_token(self, user_id):
        """
        Return token for the user

        Args:
            user (User)
        """

        try:
            token = Token.objects.get(user_id=user_id)

            return token.key
        except ObjectDoesNotExist:
            token = Token.objects.create(user_id=user_id)

            return token.key

    def get(self, request, token):
        """
        GET API -> /api/v1/user/magic_link/sign_in/<token>/
        """

        service = MagicLinkService()
        key = service.get_cache_key(token)
        cache_adapter = CacheAdapter()
        value = cache_adapter.get(key)
        if value is None:
            redirect_url = service.get_default_redirect_url()

            return HttpResponseRedirect(redirect_url)
        
        value = json.loads(value)
        user_id = value['user_id']
        redirect_link = value['redirect_link']
        token = self.__get_token(user_id)
        response = service.set_cookies_in_response(
            request,
            redirect(redirect_link),
            token
        )
        cache_adapter.delete(key)

        return response


class LoginView(APIView):
    """
    Creates a token for login
    """

    def __get_token(self, user):
        """
        Return token for the user

        Args:
            user (User)
        """

        try:
            token = Token.objects.get(user=user)

            return token.key
        except ObjectDoesNotExist:
            token = Token.objects.create(user=user)

            return token.key

    def post(self, request):
        """
        POST API -> /api/v1/user/login/
        """

        serializer = LoginUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            return Response({'token': self.__get_token(user)}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    """
    Returns the user details
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user/user_details.html'

    def __get_user_from_token(self, token):
        """
        Returns user from token

        Args:
            token (str)
        """

        if token is None:
            return None

        try:
            token = Token.objects.get(key=token)

            return token.user
        except ObjectDoesNotExist:
            return None

    def get(self, request):
        """
        GET API -> /api/v1/user/details/
        """

        token = request.COOKIES.get('token', None)
        user = self.__get_user_from_token(token)

        if user is None:
            return Response({
                'is_success': False,
                'message': 'No token or incorrect token provided.'
            })
        
        return Response({
            'is_success': True,
            'username': user.username
        })
