from rest_framework import serializers
from .models import Buy, DeliveryRequest, Sale, CashLog
from django.core.cache import cache
from inventory.serializers import PhotoCardSerializer

class SaleSerializer(serializers.ModelSerializer):
    photo_card_id = PhotoCardSerializer()

    class Meta:
        model = Sale
        fields = ['id','photo_card_id', 'amount', 'price']

    def validate(self, data):
        if not self.context['request'].user.is_seller:
            raise serializers.ValidationError("판매자만 판매 가능합니다")

        if data['amount'] <= 0:
            raise serializers.ValidationError("수량은 0보다 커야합니다")
        if data['price'] <= 0:
            raise serializers.ValidationError("가격은 0보다 커야합니다")

        existing_sales = Sale.objects.filter(
            user_id=self.context['request'].user,
            photo_card_id=data['photo_card_id'],
        )

        if existing_sales.filter(amount__gt=0).exists():
            raise serializers.ValidationError("이미 판매 중인 포토카드입니다")

        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['price'] = instance.buy_price
        return data


class BuySerializer(serializers.ModelSerializer):
    sale_id = serializers.PrimaryKeyRelatedField(queryset=Sale.objects.all())
    class Meta:
        model = Buy
        fields = ['sale_id', 'amount']

    def validate(self, data):
        '''
            구매 요청 검증
            중복 요청 방지
            구매자 검증
            수량 검증
            판매 상품 검증
            캐시 검증
        '''

        sale = data['sale_id']
        if cache.get(f'sale_transaction_lock_{sale.id}'):
            raise serializers.ValidationError({"detail": "중복 요청입니다."})
        cache.set(f'sale_transaction_lock_{sale.id}', True, timeout=1)

        user = self.context['request'].user
        if not user.is_buyer:
            raise serializers.ValidationError("구매자만 구매 가능합니다")

        if data['amount'] <= 0:
            raise serializers.ValidationError("수량은 0보다 커야합니다")

        if sale.amount < data['amount']:
            raise serializers.ValidationError("판매 수량이 부족합니다")
        if not sale:
            raise serializers.ValidationError("판매 상품이 존재하지 않습니다")
        if sale.deleted_date:
            raise serializers.ValidationError("판매 상품이 삭제되었습니다")

        total_cash = user.total_cash
        if total_cash < sale.buy_price * data['amount']:
            raise serializers.ValidationError("캐시가 부족합니다")

        return data


class DeliveryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryRequest
        fields = ['id', 'buy_id', 'status', 'address', 'postal_code']

    def validate(self, data):
        '''
            본인이 구매한 포토카드만 배송 받을 수 있게
            구매에 대한 배송 요청이 있다면 중복 배송 방지
            우편번호 기본 검증 로직
        '''
        user = self.context['request'].user
        buy = data['buy_id']

        if buy.user_id != user:
            raise serializers.ValidationError("자신의 구매 내역만 배송 요청 가능합니다")

        if buy.delivery_request:
            raise serializers.ValidationError("해당 구매에 대한 배송 요청이 존재합니다")

        if len(data['postal_code']) != 5:
            raise serializers.ValidationError("우편번호는 5자리여야 합니다")

        if user.total_cash < buy.total_delivery_price:
            raise serializers.ValidationError("캐시가 부족합니다")

        return data



