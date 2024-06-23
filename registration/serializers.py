from rest_framework import serializers
from .models import CustomUser, Business

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'username', 'password', 'role','id' ]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['business_name', 'business_address', 'business_phone_number', 'lipa_number', 'business_type', 'phone_network', 'owner','id']


