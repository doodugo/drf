from django.urls import path, include
from .views import SaleView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'sales', SaleView, basename='sales')

urlpatterns = [
    path('', include(router.urls)),
]
