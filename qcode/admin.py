from django.contrib import admin

# Register your models here.
from .models import QRCode,DynamicQRCode

admin.site.register(QRCode)
admin.site.register(DynamicQRCode)