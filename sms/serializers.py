from datetime import timezone
from django.apps import apps
from rest_framework import serializers

from registration.models import Business, CustomUser
from sms.otp_service import OTPVerificationService
from .models import NetworkCredit, OTPCredit
from django.contrib.auth.password_validation import validate_password
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator


class NetworkCreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkCredit
        fields = ['id', 'credit', 'network_type']

class OTPCreditSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), write_only=True)
    business_id = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all(), write_only=True, source='business')
    otp = serializers.CharField(min_length=5, max_length=5)  # Assuming OTP is 5 digits
    otp_expiry = serializers.DateTimeField(read_only=True)

    class Meta:
        model = OTPCredit
        fields = ['id', 'user', 'business_id', 'otp', 'otp_timestamp', 'otp_expiry']
        read_only_fields = ['otp_timestamp', 'otp_expiry']

    def validate_otp(self, value):
        """
        Validate that the OTP is exactly 5 digits.
        """
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be numeric.")
        return value

    def validate(self, data):
        """
        Validate that the OTP is still valid (i.e., not expired).
        """
        otp_record = OTPCredit.objects.filter(user=data.get('user'), business=data.get('business'), otp=data.get('otp')).first()
        if otp_record and otp_record.otp_expiry < timezone.now():
            raise serializers.ValidationError("OTP has expired.")
        return data


class OTPVerifySerializer(serializers.Serializer):
    phoneNumber = serializers.CharField()
    otp = serializers.CharField(max_length=5)
    business_id = serializers.IntegerField()

    def validate(self, attrs):
        phoneNumber = attrs.get('phoneNumber')
        otp = attrs.get('otp')
        business_id = attrs.get('business_id')

        # Use the service to validate the OTP
        OTPVerificationService.verify_otp(phoneNumber, otp, business_id)

        return attrs
    
class ResendOTPSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField(max_length=15)

class PasswordResetRequestSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField(max_length=20)


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
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise serializers.ValidationError({'uid': 'Invalid value'})

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({'token': 'Invalid or expired token'})

        return attrs

    def save(self, **kwargs):
        uid = self.validated_data.get('uid')
        new_password = self.validated_data.get('new_password')

        user = CustomUser.objects.get(pk=uid)
        user.set_password(new_password)
        user.save()
        return user
