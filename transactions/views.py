from django.shortcuts import render
from rest_framework import generics
from .serializers import SaleSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Sale
from rest_framework import viewsets

class SaleView(viewsets.ModelViewSet):
    queryset = Sale.objects.filter()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)

