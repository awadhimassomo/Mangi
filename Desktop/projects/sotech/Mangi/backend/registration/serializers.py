from rest_framework import serializers
from .models import CustomUser
from .models import Role


class CustomUserSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'PhoneNumber', 'role']
