import json

from django.views import View
from django.shortcuts import redirect, render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from user.services.user_service import UserService, TokenService
from user.services.cookies_service import CookiesService
from user.forms.user_forms import LoginForm, MagicLinkForm, RegisterUserForm
from helpers.cache_adapter import CacheAdapter
from user.serializers import RegisterUserSerializer, LoginUserSerializer, \
    GenerateMagicLinkSerializer
from user.services.magic_link_service import MagicLinkService

from worker.send_email import send_email


class RegisterUserView(View):
    form_class = RegisterUserForm
    template_name = 'user/user_register_form.html'

    def __create_user(self, data):
        email = data['email']
        password = data['password']
        username = data['username']
        user_service = UserService()
        user_service.create_user(
            email=email,
            password=password,
            username=username
        )

    def get(self, request, **kwargs):
        form = self.form_class()

        return render(request, self.template_name, context={'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            self.__create_user(form.cleaned_data)
            messages.success(request, 'User registered')

            return HttpResponseRedirect("/api/v1/user/login/")
        else:
            messages.error(
                request, 'User registration failed!')
            
            return render(request, self.template_name, context={'form': form})


class GenerateMagicLinkView(View):
    form_class = MagicLinkForm
    template_name = 'user/magic_link_form.html'

    def get(self, request, **kwargs):
        form = self.form_class()

        return render(request, self.template_name, context={'form': form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            user_service = UserService()
            user = user_service.get_user(email=email)
            magic_link_service = MagicLinkService()
            res = magic_link_service.generate_magic_link(
                request,
                user,
                "/api/v1/user/details/"
            )

            if not res['is_success']:
                messages.error(
                    request, 'Link generation failed!')
                
                return render(request, self.template_name, context={'form': form})
            
            send_email.delay(res['email'], res['content'])
            messages.error(
                request, 'Magic Link sent to your email!')
        else:
            messages.error(
                request, 'Link generation failed!')
        
        return render(request, self.template_name, context={'form': form})


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


class LoginView(View):
    form_class = LoginForm
    template_name = 'user/login_form.html'

    def get(self, request, **kwargs):
        form = self.form_class()

        return render(request, self.template_name, context={'form': form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            messages.success(request, 'User logged in')
            token_service = TokenService(form.cleaned_data['email'])
            token = token_service.get_token()
            print(token)
            cookies_service = CookiesService()
            response = cookies_service.set_cookies_in_response(
                request,
                redirect("/api/v1/user/details/"),
                token
            )

            return response
        else:
            messages.error(
                request, 'User login failed!')
            
        return render(request, self.template_name, context={'form': form})


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
            'username': user.username,
            'email': user.email
        })
