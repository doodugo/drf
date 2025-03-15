from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from transactions.models import CashLog
from .serializers import RegisterSerializer
from rest_framework import views

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class TotalCashView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_cash = CashLog.total_cash(request.user.id)
        return Response({'total_cash': total_cash})
