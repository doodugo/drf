from django.db import transaction
from rest_framework import serializers

from transactions.models import CashLog
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    '''
        Signup serializer
    '''
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type']

    @transaction.atomic
    def create(self, validated_data):
        # 사용자 생성 시 중복된 사용자 체크
        if User.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError({'email': '이미 존재하는 이메일입니다.'})

        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            email=validated_data['email'],
            user_type=validated_data['user_type'],
        )
        if created:
            user.set_password(validated_data['password'])
            user.save()
            CashLog.create_welcome_cash(user)
        else:
            raise serializers.ValidationError({
                'error': '이미 존재하는 사용자입니다.'
            })

        return user
