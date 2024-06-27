from rest_framework import serializers
from .models import CustomUser, Business,Customer

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'email', 'username', 'role', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            phone_number=validated_data['phone_number'],
            email=validated_data.get('email'),
            username=validated_data.get('username'),
            role=validated_data.get('role'),
            password=validated_data['password']
        )
        return user

    def validate_phone_number(self, value):
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ['business_name', 'business_address', 'business_phone_number', 'lipa_number', 'business_type', 'phone_network', 'owner','id']



class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')

        if phone_number and password:
            user = authenticate(request=self.context.get('request'), phone_number=phone_number, password=password)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
            
            if not user.otp_verified:
                msg = 'Phone number not verified.'
                raise serializers.ValidationError(msg, code='otp_not_verified')
        else:
            msg = 'Must include "phone_number" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data



class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class BusinessListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'