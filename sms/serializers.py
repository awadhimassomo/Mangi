from rest_framework import serializers
from .models import NetworkCredit, OTPCredit
from django.contrib.auth.password_validation import validate_password

class NetworkCreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkCredit
        fields = ['id', 'credit', 'network_type']

class OTPCreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPCredit
        fields = ['id', 'user', 'credit', 'otp', 'otp_timestamp']
        read_only_fields = ['otp_timestamp']

class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField(max_length=6)


class ResendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

class PasswordResetRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate(self, attrs):
        uid = attrs.get('uid')
        token = attrs.get('token')
        new_password = attrs.get('new_password')
        
        try:
            uid = urlsafe_base64_decode(uid).decode()
            user = UserModel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            raise serializers.ValidationError({'uid': 'Invalid value'})

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({'token': 'Invalid or expired token'})

        return attrs

    def save(self, **kwargs):
        uid = self.validated_data.get('uid')
        new_password = self.validated_data.get('new_password')

        user = UserModel.objects.get(pk=uid)
        user.set_password(new_password)
        user.save()
        return user
