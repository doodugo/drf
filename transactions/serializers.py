from rest_framework import serializers
from .models import Sale

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
