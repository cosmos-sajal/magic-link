from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist

from user.serializers import RegisterUserSerializer, LoginUserSerializer


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
            # send_welcome_email.delay(
            #     request.data['email'], request.data['name'])

            return Response({'response': 'User Created!'},
                            status=status.HTTP_201_CREATED)

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



# class UserDetailView(APIView):
#     """
#     Returns the user details
#     """

#     renderer_classes = [TemplateHTMLRenderer]
#     template_name = 'user/user_detail.html'

#     def get()


