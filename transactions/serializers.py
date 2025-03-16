from rest_framework import serializers
from .models import Buy, Sale, CashLog
from django.core.cache import cache

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = ['photo_card_id','amount', 'price']

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
    class Meta:
        model = Buy
        fields = ['sale_id', 'amount']

    def validate(self, data):
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

        total_cash = CashLog.total_cash(user)
        if total_cash < sale.buy_price * data['amount']:
            raise serializers.ValidationError("캐시가 부족합니다")

        return data
