from datetime import datetime
from django.shortcuts import render
from rest_framework import generics

from rest_framework.exceptions import PermissionDenied, ValidationError
from .serializers import SaleSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Sale
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

class SalePagination(PageNumberPagination):
    page_size = 10


class SaleView(viewsets.ModelViewSet):
    queryset = Sale.objects.filter()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SalePagination

    def get_queryset(self):
        '''
            판매 쿼리셋 정렬
            order 파라미터에 따라 정렬
            default: 최신순
            order 파라미터 예시: ?order=photocard_name,created_date
            photocard_name: 포토카드 이름
            created_date: 판매 일자
        '''

        queryset = super().get_queryset()
        queryset = queryset.order_by('-created_date')
        ordering_param = self.request.query_params.get('order')

        if ordering_param:
            ordering_fields = []
            ordering_list = ordering_param.split(",")

            if "photocard_name" in ordering_list:
                ordering_fields.append("photo_card_id__name")
            elif "-photocard_name" in ordering_list:
                ordering_fields.append("-photo_card_id__name")

            if "created_date" in ordering_list:
                ordering_fields.append("created_date")
            elif "-created_date" in ordering_list:
                ordering_fields.append("-created_date")

            queryset = queryset.order_by(*ordering_fields)

        return queryset

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

        instance.deleted_date = datetime.now()
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
