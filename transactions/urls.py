from django.urls import path, include
from .views import BuyView, SaleView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'sales', SaleView, basename='sales')
router.register(r'buys', BuyView, basename='buys')

urlpatterns = [
    path('', include(router.urls)),
]
