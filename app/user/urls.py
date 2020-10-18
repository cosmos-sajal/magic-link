from django.urls import path

from user.views import RegisterUserView, LoginView, UserDetailView, GenerateMagicLinkView

app_name = 'user'

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register-user'),
    path('login/', LoginView.as_view(), name='login-user'),
    path('details/', UserDetailView.as_view(), name='login-user'),
    path('magic_link/', GenerateMagicLinkView.as_view(), name='generate-link')
]
