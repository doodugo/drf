from django.core.cache import cache
from datetime import datetime
from django.shortcuts import render
from rest_framework import generics

from rest_framework.exceptions import PermissionDenied, ValidationError
from .serializers import BuySerializer, SaleSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Buy, CashLog, Sale
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.db.models import F

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

        queryset = super().get_queryset().filter(deleted_date__isnull=True)
        queryset = queryset.select_related('photo_card_id').order_by('-created_date')

        photo_card_name_param = self.request.query_params.get('photocard_name')
        if photo_card_name_param:
            queryset = queryset.filter(photo_card_id__name__icontains=photo_card_name_param)

        artist_name_param = self.request.query_params.get('artist_name')
        if artist_name_param:
            queryset = queryset.filter(photo_card_id__artist_name__icontains=artist_name_param)

        group_name_param = self.request.query_params.get('group_name')
        if group_name_param:
            queryset = queryset.filter(photo_card_id__group_name__icontains=group_name_param)

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


class BuyPagination(PageNumberPagination):
    page_size = 10

class BuyView(viewsets.ModelViewSet):
    queryset = Buy.objects.filter()
    serializer_class = BuySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BuyPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("sale_id__photo_card_id")
        photo_card_name_param = self.request.query_params.get('photocard_name')
        if photo_card_name_param:
            queryset = queryset.filter(sale_id__photo_card_id__name__icontains=photo_card_name_param)

        artist_name_param = self.request.query_params.get('artist_name')
        if artist_name_param:
            queryset = queryset.filter(sale_id__photo_card_id__artist_name__icontains=artist_name_param)

        group_name_param = self.request.query_params.get('group_name')
        if group_name_param:
            queryset = queryset.filter(sale_id__photo_card_id__group_name__icontains=group_name_param)

        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        '''
            validate를 통해 검증 후 구매 처리
        '''

        try: 
            serializer.save(user_id=self.request.user)
            CashLog.objects.create(
                user_id=self.request.user,
                cash = -(serializer.validated_data['amount'] * serializer.validated_data['sale_id'].buy_price)
            )
            serializer.validated_data['sale_id'].amount = F('amount') - serializer.validated_data['amount']
            serializer.validated_data['sale_id'].save(update_fields=['amount'])
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(user_id=request.user)
        queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)
