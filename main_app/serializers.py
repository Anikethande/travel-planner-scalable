# serializers.py
from rest_framework import serializers
from .models import Checking

class CheckingFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checking
        fields = '__all__'
