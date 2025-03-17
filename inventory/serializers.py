from .models import PhotoCard
from rest_framework import serializers

class PhotoCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoCard
        fields = ['id', 'name', 'artist_name', 'group_name']
