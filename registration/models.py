# registration/models.py
from django.db import models
from rest_framework import viewsets, status
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
import qrcode
import json
import logging
from io import BytesIO
from django.core.files import File
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

class Role(models.Model):
    ADMIN = 'admin'
    MANAGER = 'manager'
    CASHIER = 'cashier'
    STOREKEEPER = 'storekeeper'
    INVENTORY_MANAGER = 'inventory_manager'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (CASHIER, 'Cashier'),
        (STOREKEEPER, 'Storekeeper'),
        (INVENTORY_MANAGER, 'Inventory Manager'),
    ]
    
    name = models.CharField(max_length=100, choices=ROLE_CHOICES, default=ADMIN)
    
    def __str__(self):
        return self.get_name_display()

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    email = models.EmailField(blank=True, null=True, unique=False)
    role = models.ForeignKey('Role', on_delete=models.PROTECT, null=True, default=1)
    username = models.CharField(max_length=150, unique=True, null=True)
    is_staff = models.BooleanField(default=False)
    id = models.AutoField(primary_key=True)
    vcard_qr_image = models.ImageField(upload_to='vcards/', blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number

    def generate_vcard(self):
        vcard = f"""
BEGIN:VCARD
VERSION:3.0
FN:{self.username or ''}
TEL:{self.phone_number or ''}
EMAIL:{self.email or ''}
END:VCARD
"""
        return vcard

    def generate_vcard_qr_code(self):
        vcard = self.generate_vcard()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(vcard)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Use phone number as the file name
        temp_name = f"vcard-{self.phone_number}.png"
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        logger.info(f"vCard QR code generated, saving to {temp_name}")

        self.vcard_qr_image.save(temp_name, File(buffer), save=False)
        buffer.close()
        logger.info(f"vCard QR code saved to {self.vcard_qr_image.path}")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.vcard_qr_image:
            logger.info("No vCard QR code found, generating new one.")
            self.generate_vcard_qr_code()
        else:
            logger.info("vCard QR code already exists, skipping generation.")

class Business(models.Model):
    business_name = models.CharField(max_length=255)
    business_address = models.CharField(max_length=255)
    business_phone_number = models.CharField(max_length=20, null=True, blank=True)
    lipa_number = models.CharField(max_length=15, blank=True, null=True)
    business_type = models.CharField(max_length=100, blank=True, null=True)
    phone_network = models.CharField(max_length=10, null=True, blank=True)
    website = models.URLField(blank=True, null=True)  # Add website field
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    has_benefited_from_offer = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.qr_image:
            self.generate_qr_code()

    def generate_qr_code(self):
        # Create vCard content
        vcard = f"""
BEGIN:VCARD
VERSION:3.0
FN:{self.business_name}
ORG:{self.business_name}
TEL:{self.business_phone_number}
ADR;TYPE=WORK,PREF:;;{self.business_address};;;
URL:{self.website}
END:VCARD
"""
        print(f"Generating QR code for vCard:\n{vcard}")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(vcard)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        temp_name = f"qr-{self.pk}.png"
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        print(f"QR code generated, saving to {temp_name}")

        self.qr_image.save(temp_name, File(buffer), save=False)
        buffer.close()
        super().save(update_fields=['qr_image'])

        qr_code_path = self.qr_image.path
        print(f"QR code file saved at: {qr_code_path}")

    def __str__(self):
        return self.business_name if self.business_name else 'Unnamed Business'


class Customer(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
   

    def __str__(self):
        return self.name