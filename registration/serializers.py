from rest_framework import serializers
from .models import CustomUser, Business,Customer

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'username', 'role','id' ]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['business_name', 'business_address', 'business_phone_number', 'lipa_number', 'business_type', 'phone_network', 'owner','id']



class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)



class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


