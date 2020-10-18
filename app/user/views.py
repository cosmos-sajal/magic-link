from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from user.serializers import RegisterUserSerializer


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


