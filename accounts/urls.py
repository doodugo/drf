from django.urls import path
from .views import RegisterView, TotalCashView
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path('signup/', RegisterView.as_view(), name='signup'),
    path('signin/', TokenObtainPairView.as_view(), name='signin'),
    path('total-cash/', TotalCashView.as_view(), name='total-cash'),
]
