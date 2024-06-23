from django.contrib import admin
from .models import NetworkCredit, OTPCredit,BenefitedPhoneNumber

admin.site.register(NetworkCredit)
admin.site.register(OTPCredit)
admin.site.register(BenefitedPhoneNumber)
