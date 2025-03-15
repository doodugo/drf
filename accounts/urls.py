from django.urls import path
from .views import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path('signup/', RegisterView.as_view(), name='signup'),
    path('signin/', TokenObtainPairView.as_view(), name='signin'),
]
