from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class NetworkCredit(models.Model):
    NETWORK_CHOICES = [
        ('voda', 'Vodacom'),
        ('airtel', 'Airtel'),
        ('tigo', 'Tigo'),
        ('zantel', 'Zantel'),
        ('ttcl', 'TTCL'),
        ('halotel', 'Halotel'),
    ]

    credit = models.CharField(max_length=20, unique=True)
    network_type = models.CharField(max_length=10, choices=NETWORK_CHOICES)
    sent_timestamp = models.DateTimeField(null=True, blank=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Credit: {self.credit} - Network Type: {self.get_network_type_display()}"



class OTPCredit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE)
    otp_timestamp = models.DateTimeField(auto_now_add=True)
    otp_expiry = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.pk:
            # Only set otp_expiry if it's a new object
            self.otp_expiry = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"User: {self.user.phoneNumber} - OTP: {self.otp} - Business: {self.business.businessName if self.business else 'None'}"

class BenefitedPhoneNumber(models.Model):
    phoneNumber = models.CharField(max_length=15, unique=True)
    benefited_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phoneNumber