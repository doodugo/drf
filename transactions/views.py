from datetime import timezone
from django.shortcuts import render
from rest_framework import generics

from rest_framework.exceptions import PermissionDenied, ValidationError
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

    def update(self, request, *args, **kwargs):
        return Response(
            data={"message": "판매 상태를 수정 할 수 없습니다"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def perform_destroy(self, instance):
        if instance.user_id != self.request.user:
            raise PermissionDenied("본인이 등록한 판매건만 삭제할 수 있습니다.")

        if instance.amount == 0:
            raise ValidationError("수량이 0인 판매건은 삭제할 수 없습니다.")

        instance.deleted_date = timezone.now()
        instance.save()


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            self.perform_destroy(instance)
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionDenied as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(status=204)
