# core/serializers.py

from rest_framework import serializers
from .models import *

class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = '__all__'

class ShelterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelter
        fields = '__all__'

# 나머지 모델도 동일한 방식으로 추가
