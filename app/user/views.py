from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist

from user.serializers import RegisterUserSerializer, LoginUserSerializer, \
    GenerateMagicLinkSerializer

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
            user = serializer.validated_data['user']
            send_email.delay(user.email, "abcd")

            return Response({
                'response': 'link sent to email'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


