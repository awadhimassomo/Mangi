from registration.models import Business, CustomUser
from .models import OTPCredit
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

class OTPVerificationService:

    @staticmethod
    def verify_otp(phoneNumber, otp, business_id):
        # Check if the user exists
        try:
            user = CustomUser.objects.get(phoneNumber=phoneNumber)
        except CustomUser.DoesNotExist:
            raise ValidationError("User with this phone number does not exist.")

        # Check if the business exists and is associated with the user
        try:
            business = Business.objects.get(id=business_id, owner=user)
        except Business.DoesNotExist:
            raise ValidationError("Business does not exist for this user.")

        # Check if OTP exists for the user and the specific business, and hasn't expired
        try:
            otp_record = OTPCredit.objects.get(user=user, otp=otp, business=business)
            if timezone.now() > otp_record.otp_expiry:
                raise ValidationError("OTP has expired.")
        except OTPCredit.DoesNotExist:
            raise ValidationError("Invalid OTP for the specified business.")

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Get the business type
        businessType = business.businessType

        # Return the required details
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'businessType': businessType,
        }
