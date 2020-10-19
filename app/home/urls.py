from django.urls import path

from home.views import HomeView

app_name = 'home'

urlpatterns = [
    path('', HomeView.as_view(), name='home-view'),
]
