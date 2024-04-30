from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'PhoneNumber', 'role']
