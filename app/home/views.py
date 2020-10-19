from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response


class HomeView(APIView):
    """
    Returns the user details
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'home/home.html'

    def get(self, request):
        """
        GET API -> /api/v1/home/
        """

        return Response({
            'content': 'Welcome to home screen, you are logged out.'
        })
