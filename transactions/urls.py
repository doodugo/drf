from django.urls import path, include
from .views import BuyView, DeliveryRequestView, SaleView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'sales', SaleView, basename='sales')
router.register(r'buys', BuyView, basename='buys')
router.register(r'delivery-requests', DeliveryRequestView, basename='delivery-requests')

urlpatterns = [
    path('', include(router.urls)),
]
